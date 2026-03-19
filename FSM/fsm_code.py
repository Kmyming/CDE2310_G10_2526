import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import PoseStamped

class FSMNode(Node):
    def __init__(self):
        super().__init__('fsm_controller')

        #Internal Variables
        self.state = "IDLE"
        self.marker_detected = False
        self.marker_count = 0
        self.required_markers = 2
        self.map_explored = False

        #Publishers
        self.state_pub = self.create_publisher(String, '/states', 10)
        self.current_marker_pub = self.create_publisher(PoseStamped, '/current_marker', 10)

        #Subscibers
        self.create_subscription(PoseStamped, '/aruco_pose', self.aruco_callback, 10)
        self.create_subscription(Bool, '/dock_done', self.dock_done_callback, 10)
        self.create_subscription(Bool, '/launch_done', self.launch_done_callback, 10)
        self.create_subscription(Bool, '/map_explored', self.map_explored_callback, 10)

        #Timer
        self.timer = self.create_timer(0.1, self.state_machine_loop)
        self.get_logger().info("FSM Controller Started")
        self.change_state("EXPLORE")

    def change_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
        msg = String()
        msg.data = new_state
        self.state_pub.publish(msg)
        self.get_logger().info(f"Transitioned to {new_state} state")

    def state_machine_loop(self):
        if self.state == "EXPLORE":
            if self.marker_detected:
                self.marker_detected = False
                self.change_state("DOCK")
            
            elif self.map_explored and self.marker_count >= self.required_markers:
                self.change_state("END")
            self.change_state("EXPLORE")
        else:
            if self.state == "END":
                self.get_logger().info("Mission Complete! Goodbye!")
            pass

    def aruco_callback(self, msg):
        if self.state == "EXPLORE":
            self.get_logger().info("Marker Detected")
            self.marker_detected = True
            if self.current_marker:
                self.current_marker = msg
                self.current_marker_pub.publish(self.current_marker)
    
    def dock_done_callback(self, msg):
        if msg.data and self.state == "DOCK":
            self.get_logger().info("Docking done")
            self.current_marker = None
            self.change_state("LAUNCH")
    
    def launch_done_callback(self, msg):
        if msg.data and self.state == "LAUNCH":
            self.get_logger().info("Launch done")
            self.marker_count += 1
            self.change_state("EXPLORE")

    def map_explored_callback(self, msg):
            self.map_explored = msg.data

def main(args=None):
    rclpy.init(args=args)
    node = FSMNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()        
    
if __name__ == "__main__":
    main()