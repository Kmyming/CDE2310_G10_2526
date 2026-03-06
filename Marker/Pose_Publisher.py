#!/usr/bin/env python3
import json
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image, CameraInfo
from std_msgs.msg import String

from cv_bridge import CvBridge
import numpy as np
import cv2


class ArucoPoseStreamer(Node):
    def __init__(self):
        super().__init__("aruco_pose_streamer")

        # ---- Parameters ----
        self.declare_parameter("image_topic", "/image_raw")
        self.declare_parameter("camera_info_topic", "/camera_info")
        self.declare_parameter("marker_size_m", 0.05)  # marker side length in meters
        self.declare_parameter("dictionary", "DICT_6X6_250")
        # --------------------

        self.image_topic = self.get_parameter("image_topic").value
        self.camera_info_topic = self.get_parameter("camera_info_topic").value
        self.marker_size_m = float(self.get_parameter("marker_size_m").value)
        dict_name = self.get_parameter("dictionary").value

        self.bridge = CvBridge()

        # Publish JSON only (poses not needed)
        self.pub_debug = self.create_publisher(String, "/aruco/debug", 10)

        # Camera intrinsics / distortion
        self.K = None
        self.D = None
        self._warned_bad_camerainfo = False
        self._used_fallback_intrinsics = False

        # Subscriptions
        self.create_subscription(CameraInfo, self.camera_info_topic, self.camera_info_cb, 10)
        self.create_subscription(Image, self.image_topic, self.image_cb, 10)

        # ArUco dict + params
        self.aruco_dict = self._get_aruco_dict(dict_name)
        if hasattr(cv2.aruco, "DetectorParameters_create"):
            self.aruco_params = cv2.aruco.DetectorParameters_create()
        else:
            self.aruco_params = cv2.aruco.DetectorParameters()

        # Heartbeat timer (1 Hz)
        self.timer = self.create_timer(1.0, self.heartbeat)

        self.get_logger().info(
            f"ArUco streamer (ID+tvec+rvec). image={self.image_topic}, camera_info={self.camera_info_topic}, "
            f"marker_size_m={self.marker_size_m}, dict={dict_name}"
        )

    # -------------------- Heartbeat --------------------
    def heartbeat(self):
        msg = String()
        msg.data = json.dumps({"status": "running", "node": "aruco_pose_streamer"})
        self.pub_debug.publish(msg)

    # -------------------- ArUco dictionary --------------------
    def _get_aruco_dict(self, name: str):
        mapping = {
            "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
            "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
            "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
            "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
            "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
            "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
            "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
            "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
            "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
            "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
            "DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11,
        }
        if name not in mapping:
            self.get_logger().warn(f"Unknown dictionary '{name}', using DICT_6X6_250")
            return cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        return cv2.aruco.getPredefinedDictionary(mapping[name])

    # -------------------- CameraInfo callback --------------------
    def camera_info_cb(self, msg: CameraInfo):
        K = np.array(msg.k, dtype=np.float64).reshape((3, 3))
        D = np.array(msg.d, dtype=np.float64) if len(msg.d) > 0 else np.array([], dtype=np.float64)

        # Many camera drivers publish "empty" CameraInfo (all zeros). Detect that and ignore it.
        if K[0, 0] == 0.0 or K[1, 1] == 0.0:
            if not self._warned_bad_camerainfo:
                self.get_logger().warn(
                    "Received /camera_info but intrinsics are invalid (fx/fy are 0). "
                    "Will use a fallback pinhole model from image size instead."
                )
                self._warned_bad_camerainfo = True
            # Don't overwrite any good K/D we might have already set
            return

        self.K = K
        # If distortion is missing, assume no distortion (zeros)
        if D.size == 0:
            self.D = np.zeros((5,), dtype=np.float64)
        else:
            self.D = D

        self.get_logger().info("Received valid camera calibration (/camera_info).")

    # -------------------- Fallback intrinsics --------------------
    def _ensure_fallback_intrinsics(self, frame):
        """
        Quick workaround when /camera_info is invalid:
        build a rough pinhole model using image width/height.
        """
        if self.K is not None and self.D is not None and self.K[0, 0] != 0.0 and self.K[1, 1] != 0.0:
            return

        h, w = frame.shape[:2]

        # Rough focal length guess; works for getting non-zero tvec and reasonable relative motion.
        fx = fy = 0.9 * w
        cx = w / 2.0
        cy = h / 2.0

        self.K = np.array([[fx, 0.0, cx],
                           [0.0, fy, cy],
                           [0.0, 0.0, 1.0]], dtype=np.float64)

        # Assume no lens distortion
        self.D = np.zeros((5,), dtype=np.float64)

        if not self._used_fallback_intrinsics:
            self.get_logger().warn(
                f"Using FALLBACK intrinsics: fx=fy={fx:.1f}, cx={cx:.1f}, cy={cy:.1f}, D=zeros(5). "
                "For accurate pose, calibrate camera and publish real /camera_info."
            )
            self._used_fallback_intrinsics = True

    # -------------------- Image callback --------------------
    def image_cb(self, msg: Image):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f"cv_bridge failed: {e}")
            return

        # Ensure we have usable intrinsics (either real /camera_info or fallback)
        self._ensure_fallback_intrinsics(frame)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        corners, ids, _ = cv2.aruco.detectMarkers(
            gray,
            self.aruco_dict,
            parameters=self.aruco_params
        )

        if ids is None or len(ids) == 0:
            return

        # Pose estimate uses K and D
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
            corners, self.marker_size_m, self.K, self.D
        )

        marker_list = []
        for i, marker_id in enumerate(ids.flatten().tolist()):
            tvec = tvecs[i].reshape(3)
            rvec = rvecs[i].reshape(3)

            # Convert rvec components to degrees for printing
            rvec_deg = np.degrees(rvec)

            marker_list.append({
                "id": int(marker_id),
                "tvec_m": {"x": float(tvec[0]), "y": float(tvec[1]), "z": float(tvec[2])},
                "rvec_rad": {"x": float(rvec[0]), "y": float(rvec[1]), "z": float(rvec[2])}
            })

            # Print like earlier (ID + tvec), plus rvec in degrees
            self.get_logger().info(
                f"ID={marker_id}  "
                f"x={tvec[0]:+.3f}  y={tvec[1]:+.3f}  z={tvec[2]:+.3f}  "
                f"rx={rvec_deg[0]:+.1f}°  ry={rvec_deg[1]:+.1f}°  rz={rvec_deg[2]:+.1f}°"
            )

        out = String()
        out.data = json.dumps({
            "frame_id": msg.header.frame_id,
            "markers": marker_list
        })
        self.pub_debug.publish(out)


def main():
    rclpy.init()
    node = ArucoPoseStreamer()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
