#!/usr/bin/env python3

import math
import numpy as np
import cv2

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import TransformStamped
from cv_bridge import CvBridge
from tf2_ros import TransformBroadcaster


def rotation_matrix_to_quaternion(R: np.ndarray):
    """
    Convert a 3x3 rotation matrix into quaternion (x, y, z, w).
    """
    q = np.empty((4,), dtype=np.float64)
    trace = np.trace(R)

    if trace > 0.0:
        s = math.sqrt(trace + 1.0) * 2.0
        q[3] = 0.25 * s
        q[0] = (R[2, 1] - R[1, 2]) / s
        q[1] = (R[0, 2] - R[2, 0]) / s
        q[2] = (R[1, 0] - R[0, 1]) / s
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = math.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2.0
        q[3] = (R[2, 1] - R[1, 2]) / s
        q[0] = 0.25 * s
        q[1] = (R[0, 1] + R[1, 0]) / s
        q[2] = (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] > R[2, 2]:
        s = math.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2.0
        q[3] = (R[0, 2] - R[2, 0]) / s
        q[0] = (R[0, 1] + R[1, 0]) / s
        q[1] = 0.25 * s
        q[2] = (R[1, 2] + R[2, 1]) / s
    else:
        s = math.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2.0
        q[3] = (R[1, 0] - R[0, 1]) / s
        q[0] = (R[0, 2] + R[2, 0]) / s
        q[1] = (R[1, 2] + R[2, 1]) / s
        q[2] = 0.25 * s

    return float(q[0]), float(q[1]), float(q[2]), float(q[3])


class ArucoTFBroadcaster(Node):
    def __init__(self):
        super().__init__("aruco_tf_broadcaster")

        # -------- Hardcoded configuration --------
        self.image_topic = "/image_raw"
        self.camera_info_topic = "/camera_info"
        self.camera_frame = "camera_optical_frame"

        # Your marker settings
        self.marker_size_m = 0.05   # 5 cm
        self.aruco_dict_id = cv2.aruco.DICT_6X6_250

        # Whether to use backup calibration if /camera_info is empty/unavailable
        self.use_fallback_calibration = True

        # -------- CV / TF tools --------
        self.bridge = CvBridge()
        self.tf_broadcaster = TransformBroadcaster(self)

        # -------- Calibration state --------
        self.camera_matrix = None
        self.dist_coeffs = None
        self.have_camera_info = False
        self.logged_fallback_once = False
        self.logged_camera_info_once = False

        # -------- Fallback Pi Camera v2 calibration --------
        # Approximate backup calibration for 640x480 usage.
        # Replace with real calibration later for better accuracy.
        self.fallback_camera_matrix = np.array([
            [615.0,   0.0, 320.0],
            [  0.0, 615.0, 240.0],
            [  0.0,   0.0,   1.0]
        ], dtype=np.float64)

        self.fallback_dist_coeffs = np.array(
            [-0.05, 0.02, 0.0, 0.0, 0.0],
            dtype=np.float64
        )

        # -------- ArUco detector setup --------
        self.dictionary = cv2.aruco.getPredefinedDictionary(self.aruco_dict_id)

        if hasattr(cv2.aruco, "DetectorParameters"):
            self.detector_params = cv2.aruco.DetectorParameters()
        else:
            self.detector_params = cv2.aruco.DetectorParameters_create()

        if hasattr(cv2.aruco, "ArucoDetector"):
            self.detector = cv2.aruco.ArucoDetector(self.dictionary, self.detector_params)
        else:
            self.detector = None

        # -------- ROS subscriptions --------
        self.create_subscription(
            CameraInfo,
            self.camera_info_topic,
            self.camera_info_callback,
            qos_profile_sensor_data
        )

        self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            qos_profile_sensor_data
        )

        self.get_logger().info("Aruco TF broadcaster started")
        self.get_logger().info(f"Image topic: {self.image_topic}")
        self.get_logger().info(f"Camera info topic: {self.camera_info_topic}")
        self.get_logger().info(f"Camera frame: {self.camera_frame}")
        self.get_logger().info("ArUco dictionary: DICT_6X6_250")
        self.get_logger().info(f"Marker size: {self.marker_size_m} m")

    def camera_info_callback(self, msg: CameraInfo):
        """
        Save calibration from /camera_info if valid.
        """
        if len(msg.k) == 9 and any(v != 0.0 for v in msg.k):
            self.camera_matrix = np.array(msg.k, dtype=np.float64).reshape(3, 3)
            self.dist_coeffs = np.array(msg.d, dtype=np.float64)
            self.have_camera_info = True

            if not self.logged_camera_info_once:
                self.get_logger().info("Using calibration from /camera_info")
                self.logged_camera_info_once = True
        else:
            self.have_camera_info = False

    def get_calibration(self):
        """
        Return (camera_matrix, dist_coeffs, source_name)
        """
        if self.have_camera_info and self.camera_matrix is not None:
            return self.camera_matrix, self.dist_coeffs, "camera_info"

        if self.use_fallback_calibration:
            if not self.logged_fallback_once:
                self.get_logger().warn("No valid /camera_info found, using fallback calibration")
                self.logged_fallback_once = True
            return self.fallback_camera_matrix, self.fallback_dist_coeffs, "fallback"

        return None, None, "none"

    def detect_markers(self, gray):
        if self.detector is not None:
            corners, ids, rejected = self.detector.detectMarkers(gray)
        else:
            corners, ids, rejected = cv2.aruco.detectMarkers(
                gray,
                self.dictionary,
                parameters=self.detector_params
            )
        return corners, ids, rejected

    def image_callback(self, msg: Image):
        camera_matrix, dist_coeffs, calib_source = self.get_calibration()

        if camera_matrix is None or dist_coeffs is None:
            self.get_logger().warning("No calibration available, skipping frame")
            return

        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f"Failed to convert image: {e}")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.detect_markers(gray)

        if ids is None or len(ids) == 0:
            return

        try:
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners,
                self.marker_size_m,
                camera_matrix,
                dist_coeffs
            )
        except Exception as e:
            self.get_logger().error(f"Pose estimation failed: {e}")
            return

        ids = ids.flatten()

        for i, marker_id in enumerate(ids):
            rvec = rvecs[i][0]
            tvec = tvecs[i][0]

            rot_mat, _ = cv2.Rodrigues(rvec)
            qx, qy, qz, qw = rotation_matrix_to_quaternion(rot_mat)

            transform = TransformStamped()
            transform.header.stamp = msg.header.stamp
            transform.header.frame_id = self.camera_frame
            transform.child_frame_id = f"aruco_marker_{int(marker_id)}"

            transform.transform.translation.x = float(tvec[0])
            transform.transform.translation.y = float(tvec[1])
            transform.transform.translation.z = float(tvec[2])

            transform.transform.rotation.x = qx
            transform.transform.rotation.y = qy
            transform.transform.rotation.z = qz
            transform.transform.rotation.w = qw

            


def main(args=None):
    rclpy.init(args=args)
    node = ArucoTFBroadcaster()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()