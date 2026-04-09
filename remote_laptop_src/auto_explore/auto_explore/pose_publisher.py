#!/usr/bin/env python3
import json
import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import TransformStamped
from std_msgs.msg import String, Bool

from cv_bridge import CvBridge
import numpy as np
import cv2
from tf2_ros import TransformBroadcaster


def rotation_matrix_to_quaternion(rotation_matrix: np.ndarray):
    q = np.empty((4,), dtype=np.float64)
    trace = np.trace(rotation_matrix)

    if trace > 0.0:
        s = math.sqrt(trace + 1.0) * 2.0
        q[3] = 0.25 * s
        q[0] = (rotation_matrix[2, 1] - rotation_matrix[1, 2]) / s
        q[1] = (rotation_matrix[0, 2] - rotation_matrix[2, 0]) / s
        q[2] = (rotation_matrix[1, 0] - rotation_matrix[0, 1]) / s
    elif rotation_matrix[0, 0] > rotation_matrix[1, 1] and rotation_matrix[0, 0] > rotation_matrix[2, 2]:
        s = math.sqrt(1.0 + rotation_matrix[0, 0] - rotation_matrix[1, 1] - rotation_matrix[2, 2]) * 2.0
        q[3] = (rotation_matrix[2, 1] - rotation_matrix[1, 2]) / s
        q[0] = 0.25 * s
        q[1] = (rotation_matrix[0, 1] + rotation_matrix[1, 0]) / s
        q[2] = (rotation_matrix[0, 2] + rotation_matrix[2, 0]) / s
    elif rotation_matrix[1, 1] > rotation_matrix[2, 2]:
        s = math.sqrt(1.0 + rotation_matrix[1, 1] - rotation_matrix[0, 0] - rotation_matrix[2, 2]) * 2.0
        q[3] = (rotation_matrix[0, 2] - rotation_matrix[2, 0]) / s
        q[0] = (rotation_matrix[0, 1] + rotation_matrix[1, 0]) / s
        q[1] = 0.25 * s
        q[2] = (rotation_matrix[1, 2] + rotation_matrix[2, 1]) / s
    else:
        s = math.sqrt(1.0 + rotation_matrix[2, 2] - rotation_matrix[0, 0] - rotation_matrix[1, 1]) * 2.0
        q[3] = (rotation_matrix[1, 0] - rotation_matrix[0, 1]) / s
        q[0] = (rotation_matrix[0, 2] + rotation_matrix[2, 0]) / s
        q[1] = (rotation_matrix[1, 2] + rotation_matrix[2, 1]) / s
        q[2] = 0.25 * s

    return float(q[0]), float(q[1]), float(q[2]), float(q[3])


class ArucoPoseStreamer(Node):
    def __init__(self):
        super().__init__('aruco_pose_streamer')

        self.declare_parameter('image_topic', '/camera/image_raw')
        self.declare_parameter('camera_info_topic', '/camera/camera_info')
        self.declare_parameter('camera_frame', 'camera_optical_frame')
        self.declare_parameter('marker_size_m', 0.053)
        self.declare_parameter('dictionary', 'DICT_4X4_250')

        self.image_topic = self.get_parameter('image_topic').value
        self.camera_info_topic = self.get_parameter('camera_info_topic').value
        self.camera_frame = self.get_parameter('camera_frame').value
        self.marker_size_m = float(self.get_parameter('marker_size_m').value)
        dict_name = self.get_parameter('dictionary').value

        self.bridge = CvBridge()
        self.tf_broadcaster = TransformBroadcaster(self)

        self.pub_debug = self.create_publisher(String, '/aruco/debug', 10)
        self.marker_detected_pub = self.create_publisher(Bool, '/marker_detected', 10)

        self.K = None
        self.D = None
        self._warned_bad_camerainfo = False
        self._used_fallback_intrinsics = False

        self.create_subscription(CameraInfo, self.camera_info_topic, self.camera_info_cb, qos_profile_sensor_data)
        self.create_subscription(Image, self.image_topic, self.image_cb, qos_profile_sensor_data)

        self.aruco_dict = self._get_aruco_dict(dict_name)
        if hasattr(cv2.aruco, 'DetectorParameters_create'):
            self.aruco_params = cv2.aruco.DetectorParameters_create()
        else:
            self.aruco_params = cv2.aruco.DetectorParameters()

        self.timer = self.create_timer(1.0, self.heartbeat)
        self._marker_visible = None

        self.get_logger().info(
            f'ArUco streamer started image={self.image_topic}, camera_info={self.camera_info_topic}, '
            f'marker_size_m={self.marker_size_m}, dict={dict_name}'
        )

    def heartbeat(self):
        msg = String()
        msg.data = json.dumps({'status': 'running', 'node': 'aruco_pose_streamer'})
        self.pub_debug.publish(msg)

    def _get_aruco_dict(self, name: str):
        mapping = {
            'DICT_4X4_50': cv2.aruco.DICT_4X4_50,
            'DICT_4X4_100': cv2.aruco.DICT_4X4_100,
            'DICT_4X4_250': cv2.aruco.DICT_4X4_250,
            'DICT_4X4_1000': cv2.aruco.DICT_4X4_1000,
            'DICT_5X5_50': cv2.aruco.DICT_5X5_50,
            'DICT_5X5_100': cv2.aruco.DICT_5X5_100,
            'DICT_6X6_50': cv2.aruco.DICT_6X6_50,
            'DICT_6X6_100': cv2.aruco.DICT_6X6_100,
            'DICT_6X6_250': cv2.aruco.DICT_6X6_250,
            'DICT_6X6_1000': cv2.aruco.DICT_6X6_1000,
            'DICT_APRILTAG_36h11': cv2.aruco.DICT_APRILTAG_36h11,
        }
        if name not in mapping:
            self.get_logger().warn(f"Unknown dictionary '{name}', using DICT_4X4_250")
            return cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
        return cv2.aruco.getPredefinedDictionary(mapping[name])

    def camera_info_cb(self, msg: CameraInfo):
        K = np.array(msg.k, dtype=np.float64).reshape((3, 3))
        D = np.array(msg.d, dtype=np.float64) if len(msg.d) > 0 else np.array([], dtype=np.float64)

        if K[0, 0] == 0.0 or K[1, 1] == 0.0:
            if not self._warned_bad_camerainfo:
                self.get_logger().warn(
                    'Received /camera_info with invalid intrinsics (fx/fy=0); using fallback pinhole model.'
                )
                self._warned_bad_camerainfo = True
            return

        self.K = K
        self.D = np.zeros((5,), dtype=np.float64) if D.size == 0 else D

    def _ensure_fallback_intrinsics(self, frame):
        if self.K is not None and self.D is not None and self.K[0, 0] != 0.0 and self.K[1, 1] != 0.0:
            return

        h, w = frame.shape[:2]
        fx = fy = 0.9 * w
        cx = w / 2.0
        cy = h / 2.0

        self.K = np.array([
            [fx, 0.0, cx],
            [0.0, fy, cy],
            [0.0, 0.0, 1.0],
        ], dtype=np.float64)
        self.D = np.zeros((5,), dtype=np.float64)

        if not self._used_fallback_intrinsics:
            self.get_logger().warn('Using fallback camera intrinsics for ArUco pose.')
            self._used_fallback_intrinsics = True

    def image_cb(self, msg: Image):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as exc:
            self.get_logger().error(f'cv_bridge failed: {exc}')
            self._publish_marker_detected(False)
            return

        self._ensure_fallback_intrinsics(frame)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(
            gray,
            self.aruco_dict,
            parameters=self.aruco_params,
        )

        if ids is None or len(ids) == 0:
            self._publish_marker_detected(False)
            return

        try:
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners,
                self.marker_size_m,
                self.K,
                self.D,
            )
        except Exception as exc:
            self.get_logger().error(f'Pose estimation failed: {exc}')
            self._publish_marker_detected(False)
            return

        marker_list = []
        self._publish_marker_detected(True)

        frame_id = msg.header.frame_id if msg.header.frame_id else self.camera_frame

        for i, marker_id in enumerate(ids.flatten().tolist()):
            tvec = tvecs[i].reshape(3)
            rvec = rvecs[i].reshape(3)

            rot_mat, _ = cv2.Rodrigues(rvec)
            qx, qy, qz, qw = rotation_matrix_to_quaternion(rot_mat)

            transform = TransformStamped()
            transform.header.stamp = self.get_clock().now().to_msg()
            transform.header.frame_id = frame_id
            transform.child_frame_id = f'aruco_marker_{int(marker_id)}'
            transform.transform.translation.x = float(tvec[0])
            transform.transform.translation.y = float(tvec[1])
            transform.transform.translation.z = float(tvec[2])
            transform.transform.rotation.x = qx
            transform.transform.rotation.y = qy
            transform.transform.rotation.z = qz
            transform.transform.rotation.w = qw
            self.tf_broadcaster.sendTransform(transform)

            marker_list.append({
                'id': int(marker_id),
                'tvec_m': {'x': float(tvec[0]), 'y': float(tvec[1]), 'z': float(tvec[2])},
                'rvec_rad': {'x': float(rvec[0]), 'y': float(rvec[1]), 'z': float(rvec[2])},
            })

        out = String()
        out.data = json.dumps({'frame_id': frame_id, 'markers': marker_list})
        self.pub_debug.publish(out)

    def _publish_marker_detected(self, visible: bool):
        if self._marker_visible == visible:
            return

        self._marker_visible = visible
        self.marker_detected_pub.publish(Bool(data=visible))


def main():
    rclpy.init()
    node = ArucoPoseStreamer()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
