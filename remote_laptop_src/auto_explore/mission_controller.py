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

        # Store incoming velocities
        self.latest_nav = Twist()
        self.latest_dock = Twist()

        # Publishers
        self.state_pub = self.create_publisher(String, '/states', 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.zone_pub = self.create_publisher(String, '/zone', 10)

        # Subscribers (FSM triggers)
        self.create_subscription(Bool, '/dock_done', self.dock_done_callback, 10)
        self.create_subscription(Bool, '/launch_done', self.launch_done_callback, 10)
        self.create_subscription(Bool, '/map_explored', self.map_explored_callback, 10)
        self.create_subscription(Bool, '/marker_detected', self.aruco_callback, 10)
        self.create_subscription(TFMessage, '/tf', self.tf_callback, 10)

        # Subscribers (velocity inputs)
        self.create_subscription(Twist, '/cmd_vel_nav', self.nav_cb, 10)
        self.create_subscription(Twist, '/cmd_vel_docking', self.dock_cb, 10)

        # Main loop
        self.timer = self.create_timer(0.1, self.state_machine_loop)
        self.change_state("EXPLORE")

    # TF callback (extract zone from marker id)
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
                    continue

                self.current_zone = zone
                return

    # Velocity callbacks
    def nav_cb(self, msg):
        self.latest_nav = msg

    def dock_cb(self, msg):
        self.latest_dock = msg

    # State transition handler
    def change_state(self, new_state):
        if self.state == new_state:
            return

        self.state = new_state

        msg = String()
        msg.data = new_state
        self.state_pub.publish(msg)

        # Publish zone only during DOCK and LAUNCH
        if new_state in ["DOCK", "LAUNCH"] and self.current_zone:
            zone_msg = String()
            zone_msg.data = self.current_zone
            self.zone_pub.publish(zone_msg)

    # FSM loop
    def state_machine_loop(self):
        if self.state == "EXPLORE":
            if self.marker_detected and self.current_zone:
                self.marker_detected = False
                self.change_state("DOCK")

        elif self.state == "DOCK":
            # Fail check: if marker lost, go back to explore
            if not self.marker_detected:
                self.current_zone = None
                self.change_state("EXPLORE")

        elif self.state == "END":
            self.timer.cancel()

        self.publish_cmd()

    # Velocity multiplexer
    def publish_cmd(self):
        if self.state == "EXPLORE":
            self.cmd_pub.publish(self.latest_nav)
        elif self.state == "DOCK":
            self.cmd_pub.publish(self.latest_dock)
        else:
            self.cmd_pub.publish(Twist())

    # FSM trigger callbacks
    def aruco_callback(self, msg: Bool):
        self.marker_detected = msg.data

    def dock_done_callback(self, msg: Bool):
        if self.state == "DOCK":
            if msg.data:
                self.change_state("LAUNCH")
            else:
                # Dock failed → return to explore
                self.current_zone = None
                self.change_state("EXPLORE")

    def launch_done_callback(self, msg: Bool):
        if msg.data and self.state == "LAUNCH":
            # Mark visited AFTER full task completion
            if self.current_zone:
                self.visited_markers[self.current_zone] = True

            self.marker_count += 1
            self.current_zone = None
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