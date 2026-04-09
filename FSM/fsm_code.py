import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import Twist
from tf2_msgs.msg import TFMessage


class FSMNode(Node):
    def __init__(self):
        super().__init__('fsm_controller')

        # State variables
        self.state = "IDLE"
        self.marker_detected = False
        self.marker_count = 0
        self.required_markers = 2
        self.map_explored = False

        # Zone tracking
        self.current_zone = None

        # Track visited markers
        self.visited_markers = {
            "static": False,
            "dynamic": False
        }

        # Store velocities
        self.latest_nav = Twist()
        self.latest_dock = Twist()

        # Publishers
        self.state_pub = self.create_publisher(String, '/states', 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.zone_pub = self.create_publisher(String, '/zone', 10)

        # Subscribers
        self.create_subscription(Bool, '/dock_done', self.dock_done_callback, 10)
        self.create_subscription(Bool, '/launch_done', self.launch_done_callback, 10)
        self.create_subscription(Bool, '/map_explored', self.map_explored_callback, 10)
        self.create_subscription(Bool, '/marker_detected', self.aruco_callback, 10)
        self.create_subscription(TFMessage, '/tf', self.tf_callback, 10)

        self.create_subscription(Twist, '/cmd_vel_nav', self.nav_cb, 10)
        self.create_subscription(Twist, '/cmd_vel_docking', self.dock_cb, 10)

        # Loop
        self.timer = self.create_timer(0.1, self.state_machine_loop)
        self.change_state("EXPLORE")

    # -------- TF CALLBACK --------
    def tf_callback(self, msg):
        for transform in msg.transforms:
            if transform.child_frame_id.startswith('aruco_marker_'):

                if transform.child_frame_id.endswith('0'):
                    zone = "static"
                elif transform.child_frame_id.endswith('1'):
                    zone = "dynamic"
                else:
                    continue

                # Skip if already visited
                if self.visited_markers[zone]:
                    return

                self.current_zone = zone
                return

    # -------- VELOCITY --------
    def nav_cb(self, msg):
        self.latest_nav = msg

    def dock_cb(self, msg):
        self.latest_dock = msg

    # -------- STATE CHANGE --------
    def change_state(self, new_state):
        if self.state == new_state:
            return

        self.state = new_state

        msg = String()
        msg.data = new_state
        self.state_pub.publish(msg)

        # Publish zone ONLY during DOCK and LAUNCH
        if new_state in ["DOCK", "LAUNCH"] and self.current_zone is not None:
            zone_msg = String()
            zone_msg.data = self.current_zone
            self.zone_pub.publish(zone_msg)

    # -------- FSM LOOP --------
    def state_machine_loop(self):
        if self.state == "EXPLORE":
            if self.marker_detected and self.current_zone is not None:
                self.marker_detected = False
                self.change_state("DOCK")

            elif self.map_explored and self.marker_count >= self.required_markers:
                self.change_state("END")

        elif self.state == "END":
            self.timer.cancel()

        self.publish_cmd()

    # -------- CMD VEL --------
    def publish_cmd(self):
        if self.state == "EXPLORE":
            self.cmd_pub.publish(self.latest_nav)
        elif self.state == "DOCK":
            self.cmd_pub.publish(self.latest_dock)
        else:
            self.cmd_pub.publish(Twist())

    # -------- TRIGGERS --------
    def aruco_callback(self, msg: Bool):
        if msg.data and self.state == "EXPLORE":
            self.marker_detected = True

    def dock_done_callback(self, msg: Bool):
        if msg.data and self.state == "DOCK":
            self.change_state("LAUNCH")

    def launch_done_callback(self, msg: Bool):
        if msg.data and self.state == "LAUNCH":
            
            # Mark zone as visited
            if self.current_zone is not None:
                self.visited_markers[self.current_zone] = True

            self.marker_count += 1
            self.current_zone = None  # reset
            self.change_state("EXPLORE")

    def map_explored_callback(self, msg: Bool):
        self.map_explored = msg.data


def main(args=None):
    rclpy.init(args=args)
    node = FSMNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
