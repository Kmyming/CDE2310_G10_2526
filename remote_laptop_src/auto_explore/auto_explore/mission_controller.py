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
        self.shoot_requested = False
        self.launch_completion_consumed = False

        # Zone tracking
        self.current_zone = None
        self.visited_markers = {
            'static': False,
            'dynamic': False,
        }

        # Latest velocity inputs
        self.latest_nav = Twist()
        self.latest_dock = Twist()

        # Publishers
        self.state_pub = self.create_publisher(String, '/states', 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.zone_pub = self.create_publisher(String, '/zone', 10)
        self.shoot_type_pub = self.create_publisher(String, '/shoot_type', 10)

        # Subscribers (state triggers)
        self.create_subscription(Bool, '/dock_done', self.dock_done_callback, 10)
        self.create_subscription(Bool, '/shoot_done', self.shoot_done_callback, 10)
        # Backward-compatible trigger for legacy launcher nodes.
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

    # Velocity callbacks
    def nav_cb(self, msg):
        self.latest_nav = msg

    def dock_cb(self, msg):
        self.latest_dock = msg

    def tf_callback(self, msg: TFMessage):
        for transform in msg.transforms:
            if not transform.child_frame_id.startswith('aruco_marker_'):
                continue

            zone = None
            if transform.child_frame_id.endswith('0'):
                zone = 'static'
            elif transform.child_frame_id.endswith('1'):
                zone = 'dynamic'

            if zone is None:
                continue

            if self.visited_markers.get(zone, False):
                continue

            self.current_zone = zone
            return

    # State transition handler
    def change_state(self, new_state):
        if self.state == new_state:
            return

        self.state = new_state
        
        self.get_logger().info(f"[FSM] STATE CHANGE: {self.state}")

        msg = String()
        msg.data = new_state
        self.state_pub.publish(msg)

        if new_state in ["DOCK", "LAUNCH"] and self.current_zone is not None:
            zone_msg = String()
            zone_msg.data = self.current_zone
            self.zone_pub.publish(zone_msg)

        if new_state != "LAUNCH":
            self.shoot_requested = False
            self.launch_completion_consumed = False

    # FSM loop
    def state_machine_loop(self):
        if self.state == "EXPLORE":
            if self.marker_detected and self.current_zone is not None:
                self.marker_detected = False
                self.get_logger().info("[FSM] Marker detected! Transitioning to DOCK")
                self.change_state("DOCK")
            elif self.map_explored and self.marker_count >= self.required_markers:
                self.get_logger().info("[FSM] Map fully explored and markers found. Transitioning to END")
                self.change_state("END")

        elif self.state == "LAUNCH":
            if not self.shoot_requested:
                trigger = String()
                if self.current_zone in ('static', 'dynamic'):
                    trigger.data = self.current_zone
                else:
                    trigger.data = 'auto'
                self.shoot_type_pub.publish(trigger)
                self.shoot_requested = True

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

    # FSM callbacks
    def aruco_callback(self, msg: Bool):
        if msg.data and self.state == "EXPLORE":
            self.get_logger().info("[FSM] Marker detected signal received")
            self.marker_detected = True

    def dock_done_callback(self, msg: Bool):
        if self.state != 'DOCK':
            return

        if msg.data:
            self.change_state("LAUNCH")
            return

        self.get_logger().warn('[FSM] Docking reported failure, returning to EXPLORE')
        self.marker_detected = False
        self.change_state('EXPLORE')

    def shoot_done_callback(self, msg: Bool):
        self._handle_launch_completion(msg, source='shoot_done')

    def launch_done_callback(self, msg: Bool):
        self._handle_launch_completion(msg, source='launch_done')

    def _handle_launch_completion(self, msg: Bool, source: str):
        if self.state != 'LAUNCH' or not msg.data:
            return

        if self.launch_completion_consumed:
            self.get_logger().warn(f'[FSM] Ignoring duplicate launch completion from {source}')
            return

        self.launch_completion_consumed = True

        if self.current_zone in self.visited_markers:
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
