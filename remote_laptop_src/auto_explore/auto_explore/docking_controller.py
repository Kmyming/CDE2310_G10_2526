#!/usr/bin/env python3

import math
import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool, String
from tf2_msgs.msg import TFMessage


class DockingController(Node):
    def __init__(self):
        super().__init__('docking_controller')

        # Parameters
        self.declare_parameter('target_marker_prefix', 'aruco_marker_')
        self.declare_parameter('approach_speed', 0.08)
        self.declare_parameter('max_ang_speed', 0.30)
        self.declare_parameter('align_kp', 1.8)
        self.declare_parameter('tx_tolerance', 0.02)
        self.declare_parameter('dock_distance_m', 0.12)
        self.declare_parameter('timeout_sec', 2.0)
        self.declare_parameter('dock_cycle_timeout_sec', 20.0)
        self.declare_parameter('target_marker_id', -1)
        self.declare_parameter('robot_r', 0.2)

        self.target_marker_prefix = self.get_parameter('target_marker_prefix').value
        self.approach_speed = float(self.get_parameter('approach_speed').value)
        self.max_ang_speed = float(self.get_parameter('max_ang_speed').value)
        self.align_kp = float(self.get_parameter('align_kp').value)
        self.tx_tolerance = float(self.get_parameter('tx_tolerance').value)
        self.dock_distance_m = float(self.get_parameter('dock_distance_m').value)
        self.timeout_sec = float(self.get_parameter('timeout_sec').value)
        self.dock_cycle_timeout_sec = float(self.get_parameter('dock_cycle_timeout_sec').value)
        self.target_marker_id = int(self.get_parameter('target_marker_id').value)
        self.robot_r = float(self.get_parameter('robot_r').value)

        # FSM state gate
        self.current_state = 'IDLE'

        # Marker observations (camera frame)
        self.marker_visible = False
        self.latest_tx = None
        self.latest_tz = None
        self.last_seen_time = self.get_clock().now()

        # Sensors
        self.scan = None

        # Pub/Sub
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel_docking', 10)
        self.done_pub = self.create_publisher(Bool, '/dock_done', 10)

        self.create_subscription(String, '/states', self.state_callback, 10)
        self.create_subscription(TFMessage, '/tf', self.tf_callback, 10)
        self.create_subscription(LaserScan, '/scan', self.scan_callback, qos_profile_sensor_data)

        self.timer = self.create_timer(0.05, self.control_loop)

        self._published_done_for_cycle = False
        self._dock_cycle_start = None
        self.get_logger().info('Docking controller started')

    def state_callback(self, msg: String):
        prev = self.current_state
        self.current_state = msg.data

        if self.current_state == 'DOCK' and prev != 'DOCK':
            self._dock_cycle_start = self.get_clock().now()
            self._published_done_for_cycle = False

        if self.current_state != 'DOCK' and prev == 'DOCK':
            self.cmd_pub.publish(Twist())
            self._published_done_for_cycle = False
            self._dock_cycle_start = None

    def tf_callback(self, msg: TFMessage):
        for transform in msg.transforms:
            if transform.child_frame_id.startswith(self.target_marker_prefix):
                if self.target_marker_id >= 0:
                    marker_suffix = transform.child_frame_id.split('_')[-1]
                    try:
                        marker_id = int(marker_suffix)
                    except ValueError:
                        continue

                    if marker_id != self.target_marker_id:
                        continue

                self.latest_tx = transform.transform.translation.x
                self.latest_tz = transform.transform.translation.z
                self.marker_visible = True
                self.last_seen_time = self.get_clock().now()
                return

    def scan_callback(self, msg: LaserScan):
        self.scan = msg.ranges

    def _local_avoidance(self):
        if self.scan is None or len(self.scan) == 0:
            return None, None

        s = np.array(self.scan, dtype=float)
        s = np.nan_to_num(s, nan=10.0, posinf=10.0, neginf=0.0)
        n = len(s)

        front_range = max(1, n // 12)
        front_center = s[:front_range].tolist() + s[n - front_range:].tolist()

        left_end = max(1, n // 6)
        right_start = max(0, n - n // 6)
        front_left = s[:left_end]
        front_right = s[right_start:]

        min_front = float(np.min(front_center))
        min_left = float(np.min(front_left))
        min_right = float(np.min(front_right))

        stop_dist = self.robot_r * 0.6
        avoid_dist = self.robot_r

        if min_front < stop_dist:
            return 0.0, 0.0

        if min_front < avoid_dist:
            if min_left > min_right:
                return 0.05, math.pi / 4
            return 0.05, -math.pi / 4

        return None, None

    def _marker_is_stale(self):
        dt = (self.get_clock().now() - self.last_seen_time).nanoseconds / 1e9
        return dt > self.timeout_sec

    def control_loop(self):
        if self.current_state != 'DOCK':
            return

        if self._dock_cycle_start is not None:
            elapsed = (self.get_clock().now() - self._dock_cycle_start).nanoseconds / 1e9
            if elapsed > self.dock_cycle_timeout_sec:
                self._publish_dock_result(False, f'dock timeout after {elapsed:.1f}s')
                return

        if self._marker_is_stale():
            self.marker_visible = False

        cmd = Twist()

        avoid_v, avoid_w = self._local_avoidance()
        if avoid_v is not None and avoid_w is not None:
            cmd.linear.x = avoid_v
            cmd.angular.z = avoid_w
            self.cmd_pub.publish(cmd)
            return

        if not self.marker_visible or self.latest_tx is None or self.latest_tz is None:
            # Slow in-place search until marker appears.
            cmd.angular.z = 0.20
            self.cmd_pub.publish(cmd)
            return

        if self.latest_tz <= self.dock_distance_m:
            self.cmd_pub.publish(Twist())
            self._publish_dock_result(True, 'docking complete')
            return

        # Align then approach
        tx = float(self.latest_tx)
        if abs(tx) > self.tx_tolerance:
            cmd.angular.z = max(min(self.align_kp * tx, self.max_ang_speed), -self.max_ang_speed)
            cmd.linear.x = 0.0
        else:
            cmd.linear.x = self.approach_speed
            cmd.angular.z = 0.0

        self.cmd_pub.publish(cmd)

    def _publish_dock_result(self, success: bool, reason: str):
        self.cmd_pub.publish(Twist())
        if self._published_done_for_cycle:
            return

        self.done_pub.publish(Bool(data=success))
        self._published_done_for_cycle = True

        if success:
            self.get_logger().info(f'Docking complete, published /dock_done=True ({reason})')
        else:
            self.get_logger().warn(f'Docking failed, published /dock_done=False ({reason})')


def main(args=None):
    rclpy.init(args=args)
    node = DockingController()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
