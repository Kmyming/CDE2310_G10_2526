#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import Odometry
import numpy as np
from sensor_msgs.msg import LaserScan
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import String
from std_msgs.msg import Bool



class MoveOnAruco(Node):
    def __init__(self):
        super().__init__('move_on_aruco')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.status_pub = self.create_publisher(Bool, '/dock_done', 10)
        self.tf_sub = self.create_subscription(TFMessage, '/tf', self.tf_callback, 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.subscription = self.create_subscription(
            LaserScan,
            'scan',
            self.scan_callback,
            qos_profile_sensor_data
        )

        # Latest marker data
        self.marker_visible = False
        self.last_seen_time = self.get_clock().now()
        self.timeout_sec = 2

        self.latest_tx = None
        self.latest_tz = None
        self.latest_rx = None
        self.latest_ry = None
        self.latest_rz = None
        self.latest_rw = None

        # Current odom pose
        self.curr_x = 0.0
        self.curr_y = 0.0
        self.curr_yaw = 0.0
        self.odom_ready = False

        # Motion tuning
        self.forward_speed = 0.08
        self.turn_kp = 1.8
        self.max_ang_speed = 0.25
        self.turn_tolerance = math.radians(2.0)
        self.dist_tolerance = 0.01

        # Thresholds
        self.tx_align_tolerance = 0.01     # “face marker exactly”
        self.mid_tz_threshold = 0.50       # first straight approach limit
        self.final_tz_threshold = 0.10     # final docking stop
        self.theta_min_for_manoeuvre = math.radians(2.0)
        self.tx_final_align_tolerance = 0.05

        # State machine
        self.state = "SEARCH"

        # Stored motion targets
        self.turn_target_yaw = 0.0
        self.theta = 0.0
        self.side_drive_distance = 0.0
        self.side_turn_direction = 0   # +1 or -1

        # Drive start pose
        self.drive_start_x = 0.0
        self.drive_start_y = 0.0

        #avoidance
        self.robot_r = 0.2
        self.scan_data = None
        self.scan = None
        self.special_search_prev_yaw = 0.0
        self.special_search_accum_yaw = 0.0
        self.special_search_started = False

        self.timer = self.create_timer(0.05, self.timer_callback)

        self.get_logger().info("MoveOnAruco node started")

    def tf_callback(self, msg):
        for transform in msg.transforms:
            if transform.child_frame_id.startswith('aruco_marker_'):
                self.last_seen_time = self.get_clock().now()
                self.marker_visible = True

                self.latest_tx = transform.transform.translation.x
                self.latest_tz = transform.transform.translation.z
                self.latest_rx = transform.transform.rotation.x
                self.latest_ry = transform.transform.rotation.y
                self.latest_rz = transform.transform.rotation.z
                self.latest_rw = transform.transform.rotation.w
                return

    def scan_callback(self,msg):
        self.scan_data = msg
        self.scan = msg.ranges
        self.get_logger().info(f"Front LIDAR reading: {self.get_front_lidar(msg):.3f} m")

    def get_front_lidar(self,msg):
        num_readings = len(msg.ranges)
        window = 5 
        front_indices = list(range(0, window)) + list(range(num_readings - window, num_readings))
        
        # Filter for valid readings within the LIDAR range limits
        valid_ranges = [msg.ranges[i] for i in front_indices 
            if i < num_readings and msg.range_min < msg.ranges[i] < msg.range_max]

        if not valid_ranges:
            return

        return sum(valid_ranges) / len(valid_ranges)


    def localControl(self, scan):
        v = None
        w = None

        if scan is None or len(scan) == 0:
            return v, w

        s = np.array(scan, dtype=float)
        s = np.nan_to_num(s, nan=10.0, posinf=10.0, neginf=0.0)
        n = len(s)

        # front-left: first 1/6 of scan
        left_end = max(1, n // 6)
        for i in range(0, left_end):
            if s[i] < self.robot_r:
                return 0.2, -math.pi / 4

        # front-right: last 1/6 of scan
        right_start = max(0, n - n // 6)
        for i in range(right_start, n):
            if s[i] < self.robot_r:
                return 0.2, math.pi / 4

        return v, w

    def odom_callback(self, msg):
        self.curr_x = msg.pose.pose.position.x
        self.curr_y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        self.curr_yaw = self.euler_from_quaternion(q.x, q.y, q.z, q.w)
        self.odom_ready = True

    def euler_from_quaternion(self, x, y, z, w):
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        _roll_x = math.atan2(t0, t1)

        t2 = +2.0 * (w * y - z * x)
        t2 = max(min(t2, 1.0), -1.0)
        _pitch_y = math.asin(t2)

        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)

        return yaw_z

    def quat_to_rotmat(self, qx, qy, qz, qw):
        return np.array([
            [1 - 2*(qy*qy + qz*qz),     2*(qx*qy - qz*qw),     2*(qx*qz + qy*qw)],
            [    2*(qx*qy + qz*qw), 1 - 2*(qx*qx + qz*qz),     2*(qy*qz - qx*qw)],
            [    2*(qx*qz - qy*qw),     2*(qy*qz + qx*qw), 1 - 2*(qx*qx + qy*qy)]
        ])

    def compute_theta(self, tx, tz, qx, qy, qz, qw):
        """
        theta = signed angle between marker normal and marker->camera line in top view
        """
        v = np.array([-tx, -tz], dtype=float)

        R = self.quat_to_rotmat(qx, qy, qz, qw)
        n_marker = np.array([0.0, 0.0, 1.0])   # flip sign if your setup needs it
        n_cam = R @ n_marker
        n = np.array([n_cam[0], n_cam[2]], dtype=float)

        n_norm = np.linalg.norm(n)
        v_norm = np.linalg.norm(v)

        if n_norm < 1e-9 or v_norm < 1e-9:
            return 0.0

        n = n / n_norm
        v = v / v_norm

        cross = n[0] * v[1] - n[1] * v[0]
        dot = n[0] * v[0] + n[1] * v[1]

        return math.atan2(cross, dot)

    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    def turn_to_target(self, target_yaw):
        cmd = Twist()
        error = self.normalize_angle(target_yaw - self.curr_yaw)

        if abs(error) < self.turn_tolerance:
            self.cmd_pub.publish(Twist())
            return True

        ang = self.turn_kp * error
        ang = max(min(ang, self.max_ang_speed), -self.max_ang_speed)

        cmd.angular.z = ang
        cmd.linear.x = 0.0
        self.cmd_pub.publish(cmd)
        return False

    def rotate_to_center_marker(self):
        """
        Rotate until tx ~ 0, so robot faces marker directly.
        """
        if self.latest_tx is None:
            self.cmd_pub.publish(Twist())
            return False

        tx = self.latest_tx
        cmd = Twist()

        if abs(tx) < self.tx_align_tolerance:
            self.cmd_pub.publish(Twist())
            return True

        ang = self.turn_kp * tx
        ang = max(min(ang, self.max_ang_speed), -self.max_ang_speed)

        cmd.angular.z = ang
        cmd.linear.x = 0.0
        self.cmd_pub.publish(cmd)
        return False

    def start_drive(self):
        self.drive_start_x = self.curr_x
        self.drive_start_y = self.curr_y

    def distance_travelled(self):
        return math.hypot(
            self.curr_x - self.drive_start_x,
            self.curr_y - self.drive_start_y
        )

    def plan_side_step(self):
        """
        After reaching tz < mid_tz_threshold while facing the marker:
        - compute theta
        - turn by (pi/2 - |theta|)
        - drive distance to perpendicular

        Camera is upside down, so the commanded turning sign is inverted
        here directly, instead of later during execution.
        """
        tx = self.latest_tx
        tz = self.latest_tz
        rx = self.latest_rx
        ry = self.latest_ry
        rz = self.latest_rz
        rw = self.latest_rw

        if None in [tx, tz, rx, ry, rz, rw]:
            return False

        theta = self.compute_theta(tx, tz, rx, ry, rz, rw)
        self.theta = theta

        # distance to reach the perpendicular line
        side_dist = abs(tz * math.sin(theta))
        self.side_drive_distance = side_dist

        # geometric magnitude of side-turn
        turn_by = (math.pi / 2.0) - abs(theta)

        # choose direction using theta sign, then invert for upside-down camera
        if theta >= 0.0:
            delta_yaw = -turn_by
            self.side_turn_direction = -1
        else:
            delta_yaw = +turn_by
            self.side_turn_direction = +1

        self.turn_target_yaw = self.normalize_angle(self.curr_yaw + delta_yaw)

        self.get_logger().info(
            f"Side-step plan -> theta={math.degrees(theta):.2f} deg, "
            f"turn_by={math.degrees(turn_by):.2f} deg, "
            f"delta_yaw={math.degrees(delta_yaw):.2f} deg, "
            f"side_drive={side_dist:.3f} m"
        )
        return True
    
    def set_state(self, new_state):
        if self.state == new_state:
            return

        self.state = new_state

        if new_state == "DONE":
            msg = Bool()
            msg.data = True
            self.status_pub.publish(msg)
            self.get_logger().info("Docking complete")

        elif new_state == "ABORT":
            msg = Bool()
            msg.data = False
            self.status_pub.publish(msg)
            self.get_logger().info("Aborting docking procedure")

    def timer_callback(self):
        if not self.odom_ready:
            return
        
        avoidance_vel = 0.0
        avoidance_ang = 0.0
        avoidance_vel, avoidance_ang = self.localControl(self.scan)
        if (avoidance_vel is not None and avoidance_ang is not None and self.state not in ["DONE", "FINAL_APPROACH", "SPECIAL_SEARCH", "ABORT", "OBSTACLE_AVOIDANCE"]):
            self.get_logger().info("OBSTACLE AVOIDANCE ACTIVATED")
            self.state = "OBSTACLE_AVOIDANCE"

        dt = (self.get_clock().now() - self.last_seen_time).nanoseconds / 1e9
        if dt > self.timeout_sec:
            self.marker_visible = False

        # Only stop on marker loss in states that truly need live marker feedback
        if self.state != "DONE" and not self.marker_visible:
            if self.state in ["APPROACH_1", "FINAL_APPROACH"]:
                self.cmd_pub.publish(Twist())
                self.get_logger().info(f"Marker lost -> stopped | state={self.state}")
                self.set_state("ABORT")
                return

        # -------------------------
        # SEARCH / INITIAL FACE
        # -------------------------
        if self.state == "SEARCH":
            if self.latest_tx is None or self.latest_tz is None:
                self.cmd_pub.publish(Twist())
                return

            done = self.rotate_to_center_marker()
            if done:
                self.get_logger().info("SEARCH -> APPROACH_1")
                self.state = "APPROACH_1"

        # -------------------------
        # DRIVE FORWARD UNTIL tz < mid_tz_threshold
        # -------------------------
        elif self.state == "APPROACH_1":
            tz = self.latest_tz
            if tz is None:
                self.cmd_pub.publish(Twist())
                return

            if tz < self.mid_tz_threshold:
                self.cmd_pub.publish(Twist())

                ok = self.plan_side_step()
                if not ok:
                    self.get_logger().info("Side-step plan failed")
                    return

                if self.side_drive_distance <= self.dist_tolerance or abs(self.theta) < self.theta_min_for_manoeuvre:
                    # Already basically on perpendicular, skip side-step
                    if self.theta >= 0.0:
                        self.turn_target_yaw = self.normalize_angle(self.curr_yaw - math.pi / 2.0)
                    else:
                        self.turn_target_yaw = self.normalize_angle(self.curr_yaw + math.pi / 2.0)

                    self.get_logger().info(
                        f"APPROACH_1 -> TURN_FACE_MARKER | "
                        f"theta={math.degrees(self.theta):.2f} deg, "
                        f"side_drive={self.side_drive_distance:.3f} m"
                    )
                    self.state = "TURN_FACE_MARKER"
                else:
                    self.get_logger().info(
                        f"APPROACH_1 -> TURN_SIDE | "
                        f"theta={math.degrees(self.theta):.2f} deg, "
                        f"side_drive={self.side_drive_distance:.3f} m, "
                        f"target_yaw={math.degrees(self.turn_target_yaw):.2f} deg"
                    )
                    self.state = "TURN_SIDE"
                return

            cmd = Twist()
            cmd.linear.x = self.forward_speed
            cmd.angular.z = 0.0
            self.cmd_pub.publish(cmd)

        # -------------------------
        # TURN BY (pi/2 - theta)
        # -------------------------
        elif self.state == "TURN_SIDE":
            done = self.turn_to_target(self.turn_target_yaw)
            if done:
                self.start_drive()
                self.get_logger().info("TURN_SIDE -> DRIVE_SIDE")
                self.state = "DRIVE_SIDE"

        # -------------------------
        # DRIVE TO PERPENDICULAR
        # -------------------------
        elif self.state == "DRIVE_SIDE":
            travelled = self.distance_travelled()

            if travelled >= (self.side_drive_distance - self.dist_tolerance):
                self.cmd_pub.publish(Twist())

                self.get_logger().info(
                    f"DRIVE_SIDE -> TURN_FACE_MARKER | "
                    f"travelled={travelled:.3f} m, "
                    f"side_turn_direction={self.side_turn_direction}"
                )
                self.state = "TURN_FACE_MARKER"
                return

            cmd = Twist()
            cmd.linear.x = self.forward_speed
            cmd.angular.z = 0.0
            self.cmd_pub.publish(cmd)

        # -------------------------
        # TURN pi/2 TO FACE MARKER
        # -------------------------
        elif self.state == "TURN_FACE_MARKER":
            if self.latest_tx is None:
                self.cmd_pub.publish(Twist())
                return

            tx = self.latest_tx
            cmd = Twist()

            if abs(tx) < self.tx_final_align_tolerance:
                self.cmd_pub.publish(Twist())
                self.get_logger().info("TURN_FACE_MARKER -> FINAL_APPROACH")
                self.state = "FINAL_APPROACH"
                return

            # rotate slowly in the opposite direction of the earlier side-turn
            # until marker is centred again
            cmd.linear.x = 0.0
            cmd.angular.z = -self.side_turn_direction * min(self.max_ang_speed * 0.5, self.turn_kp * abs(tx))
            self.cmd_pub.publish(cmd)

        # -------------------------
        # FINAL STRAIGHT APPROACH UNTIL tz < 0.1
        # -------------------------
        elif self.state == "FINAL_APPROACH":
            tz = self.latest_tz
            if tz is None:
                self.cmd_pub.publish(Twist())
                return

            if tz < self.final_tz_threshold:
                self.get_logger().info(f"Aruco Obstacle detected in final approach at {tz:.3f} m -> DONE")
                self.set_state("DONE")
                self.cmd_pub.publish(Twist())
                return
            
            lidar_front = self.get_front_lidar(self.scan_data)
            if lidar_front is not None and lidar_front < self.final_tz_threshold + 0.1:  # add small buffer to avoid false positives right at the threshold
                self.get_logger().info(f"Lidar Obstacle detected in final approach at {lidar_front:.3f} m -> DONE")
                self.set_state("DONE")
                self.cmd_pub.publish(Twist())
                return

            cmd = Twist()
            cmd.linear.x = self.forward_speed
            cmd.angular.z = 0.0
            self.cmd_pub.publish(cmd)

        # -------------------------
        # DONE
        # -------------------------
        elif self.state == "DONE":
            self.cmd_pub.publish(Twist())

        # -------------------------
        # ABORT
        # -------------------------
        elif self.state == "ABORT":
            self.cmd_pub.publish(Twist())

        # -------------------------
        # OBSTACLE AVOIDANCE
        # -------------------------
        elif self.state == "OBSTACLE_AVOIDANCE":
            cmd = Twist()
            cmd.linear.x = avoidance_vel
            cmd.angular.z = avoidance_ang
            self.cmd_pub.publish(cmd)
            avoidance_vel, avoidance_ang = self.localControl(self.scan)
            if avoidance_vel is None or avoidance_ang is None:
                self.get_logger().info("OBSTACLE AVOIDANCE -> SPECIAL SEARCH")
                self.state = "SPECIAL_SEARCH"
            return 

        # -------------------------
        # Special Search
        # -------------------------
        elif self.state == "SPECIAL_SEARCH":
            if not self.special_search_started:
                self.special_search_prev_yaw = self.curr_yaw
                self.special_search_accum_yaw = 0.0
                self.special_search_started = True
                self.marker_visible = False  # marker data reset for visibility
                self.get_logger().info("SPECIAL_SEARCH started")

            cmd = Twist()
            cmd.linear.x = 0.0
            cmd.angular.z = 0.3
            self.cmd_pub.publish(cmd)

            delta_yaw = self.normalize_angle(self.curr_yaw - self.special_search_prev_yaw)
            self.special_search_accum_yaw += abs(delta_yaw)
            self.special_search_prev_yaw = self.curr_yaw

            if self.marker_visible:
                self.cmd_pub.publish(Twist())
                self.special_search_started = False
                self.get_logger().info("SPECIAL_SEARCH -> SEARCH")
                self.state = "SEARCH"
                return

            if self.special_search_accum_yaw >= math.radians(350):
                self.cmd_pub.publish(Twist())
                self.special_search_started = False
                self.get_logger().info("SPECIAL_SEARCH complete: 360 done, marker not found")
                self.set_state("ABORT")
                return

    def destroy_node(self):
        self.cmd_pub.publish(Twist())
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MoveOnAruco()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()