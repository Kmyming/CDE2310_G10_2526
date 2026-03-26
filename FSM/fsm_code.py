import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool


class FSMNode(Node):
    def __init__(self):
        super().__init__('fsm_controller')

        # ── Internal Variables ──────────────────────────────────────────────
        self.state = "IDLE"
        self.marker_detected = False
        self.marker_count = 0
        self.required_markers = 3
        self.map_explored = False

        # ── Publishers ──────────────────────────────────────────────────────
        self.state_pub = self.create_publisher(String, '/states', 10)

        # ── Subscribers ─────────────────────────────────────────────────────
        self.create_subscription(Bool, '/dock_done',    self.dock_done_callback,    10)
        self.create_subscription(Bool,        '/launch_done',  self.launch_done_callback,  10)
        self.create_subscription(Bool,        '/map_explored', self.map_explored_callback, 10)

        # ── Timer ───────────────────────────────────────────────────────────
        self.timer = self.create_timer(0.1, self.state_machine_loop)
        self.get_logger().info("FSM Controller Started")
        self.change_state("EXPLORE")

    # ── State management ────────────────────────────────────────────────────

    def change_state(self, new_state):
        if self.state == new_state:
            return
        self.state = new_state
        msg = String()
        msg.data = new_state
        self.state_pub.publish(msg)
        self.get_logger().info(f"Transitioned to {new_state} state")

    # ── Main loop ───────────────────────────────────────────────────────────

    def state_machine_loop(self):
        if self.state == "EXPLORE":
            if self.marker_detected:
                self.marker_detected = False
                self.change_state("DOCK")

            elif self.map_explored and self.marker_count >= self.required_markers:
                self.change_state("END")

        elif self.state == "END":
            self.get_logger().info("Mission Complete! Goodbye!")
            self.timer.cancel()   # stop the loop so this doesn't spam the log

        # DOCK and LAUNCH transitions are driven by callbacks below,
 

    # ── ArUco callback ──────────────────────────────────────────────────────

    def aruco_callback(self, msg):
        if self.state == "EXPLORE":
            self.get_logger().info("Marker detected")
            self.marker_detected = True

    # ── Dock callback ───────────────────────────────────────────────────────

    def dock_done_callback(self, msg: Bool):
        if msg.data and self.state == "DOCK":
            self.get_logger().info("Docking complete — launching")
            self.change_state("LAUNCH")

    # ── Launch callback ──────────────────────────────────────────────────────

    def launch_done_callback(self, msg: Bool):
        if msg.data and self.state == "LAUNCH":
            self.get_logger().info("Launch complete")
            self.marker_count += 1
            self.get_logger().info(f"Markers serviced: {self.marker_count}/{self.required_markers}")
            self.change_state("EXPLORE")

    # ── Map-explored callback ────────────────────────────────────────────────

    def map_explored_callback(self, msg: Bool):
        # NOTE: control.py currently calls sys.exit() instead of publishing here.
        #       Replace that sys.exit() call in control.py with:
        #
        #           self.map_explored_pub.publish(Bool(data=True))
        #
        #       and add a publisher:
        #
        #           self.map_explored_pub = self.create_publisher(Bool, '/map_explored', 10)
        self.map_explored = msg.data


def main(args=None):
    rclpy.init(args=args)
    node = FSMNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
