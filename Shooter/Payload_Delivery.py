#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
from std_msgs.msg import Bool
import threading
import time
import pigpio
import Pinion_Rotation as pinion

class ArucoTFListener(Node):
    def __init__(self):
        super().__init__("aruco_tf_listener")

        self.status = "Idle"

        self.topic = "/tf"

        self.sub = self.create_subscription(
            TFMessage,
            self.topic,
            self.cb if self.status == "Idle" else None,
            10
        )

        # Publisher for /launch_done
        self.launch_done_pub = self.create_publisher(Bool, '/launch_done', 10)

        # optional storage for latest transform of each marker
        self.transforms_by_marker = {}

        self.get_logger().info(f"Subscribed to {self.topic}")

        # pigpio setup for SG90 gate servo
        self.gate_pin = 12
        self.gate_open_us = 500
        self.gate_close_us = 1500
        self.gate_settle_s = 0.25
        self.ball_drop_s = 0.25
        self.close_to_release_s = 0.08

        self.gate_pi = pigpio.pi()
        if not self.gate_pi.connected:
            raise RuntimeError("Could not connect to pigpiod for SG90 gate control")
        self.gate_pi.set_servo_pulsewidth(self.gate_pin, self.gate_close_us)

        # Global counter shared across all delivery modes.
        self.global_shot_count = 0

        self.dynamic_counter = 0 #Counter for dynamic delivery, to ensure we shoot only 3 times when the marker is in the correct position


    def cb(self, msg: TFMessage):
        if self.status != "Idle":
            return

        for transform_stamped in msg.transforms:
            frame_id = transform_stamped.header.frame_id
            child_frame_id = transform_stamped.child_frame_id

            tx = transform_stamped.transform.translation.x
            ty = transform_stamped.transform.translation.y
            tz = transform_stamped.transform.translation.z

            qx = transform_stamped.transform.rotation.x
            qy = transform_stamped.transform.rotation.y
            qz = transform_stamped.transform.rotation.z
            qw = transform_stamped.transform.rotation.w

            marker_id = self.extract_marker_id(child_frame_id)

            if marker_id is None:
                continue

            tf_data = {
                "frame_id": frame_id,
                "child_frame_id": child_frame_id,
                "marker_id": marker_id,
                "tx": tx,
                "ty": ty,
                "tz": tz,
                "qx": qx,
                "qy": qy,
                "qz": qz,
                "qw": qw,
            }

            self.transforms_by_marker[marker_id] = tf_data

            if marker_id == "5":
                self.status = "Engaged"
                self.static_delivery(tf_data)
                return

            elif marker_id == "10":
                self.status = "Engaged"
                self.dynamic_delivery(tf_data)
                return

            elif marker_id == "21":
                self.status = "Engaged"
                self.bonus_delivery(tf_data)
                return


    def extract_marker_id(self, child_frame_id: str):
        """
        Adjust this based on your detector's frame naming format.

        Examples this supports:
        - aruco_A     -> A
        - marker_A    -> A
        - aruco_B     -> B
        - marker_B    -> B
        """

        parts = child_frame_id.split("_")

        if len(parts) >= 2:
            return parts[-1]

        return None


    def static_delivery(self, tf_data):
        print("Static Marker")

        
        delivery2_delay = 0.2
        delivery3_delay = 8.2

        # -------- First Delivery --------
        now = time.time()
        self.shoot()
        while time.time() - now < delivery2_delay:
            pass

        # -------- Second Delivery --------
        now = time.time()
        self.shoot()
        while time.time() - now < delivery3_delay:
            pass
        
        # -------- Third Delivery --------
        self.shoot()

        # Publish to /launch_done
        msg = Bool()
        msg.data = True
        self.launch_done_pub.publish(msg)

    def dynamic_delivery(self, tf_data):
        if -0.5 < tf_data["tx"] < 0.5 and self.dynamic_counter < 3:
            self.shoot()
            self.dynamic_counter += 1

        if self.dynamic_counter < 3:
            self.status = "Idle"
            return

        # Publish to /launch_done
        msg = Bool()
        msg.data = True
        self.launch_done_pub.publish(msg)



    def bonus_delivery(self, tf_data):
        print("Bonus Marker")

        delivery_delay = 1
        bonus_counter = 0

        for bonus_counter in range(3):
            self.shoot()
            now = time.time()
            bonus_counter+=1
            while time.time() - now < delivery_delay:
                pass

        # Publish to /launch_done
        msg = Bool()
        msg.data = True
        self.launch_done_pub.publish(msg)



    def open_gate(self):
        self.gate_pi.set_servo_pulsewidth(self.gate_pin, self.gate_open_us)
        time.sleep(self.gate_settle_s)

    def close_gate(self):
        self.gate_pi.set_servo_pulsewidth(self.gate_pin, self.gate_close_us)
        time.sleep(self.gate_settle_s)

    def shoot(self):
        cycle_index = self.global_shot_count
        self.get_logger().info(f"Starting shot cycle {cycle_index + 1}")

        # Start rack pullback and gate opening in parallel.
        engage_thread = threading.Thread(target=pinion.engage_rack, args=(cycle_index,))
        engage_thread.start()

        self.open_gate()
        engage_thread.join()

        # Gate stays open briefly to allow ball drop into launcher.
        time.sleep(self.ball_drop_s)
        self.close_gate()
        time.sleep(self.close_to_release_s)

        # Release rack only after gate is safely closed.
        pinion.disengage_rack(cycle_index)

        # Advance the global shot counter only after a successful launch cycle.
        self.global_shot_count += 1
    def destroy_node(self):
        try:
            self.gate_pi.set_servo_pulsewidth(self.gate_pin, 0)
            self.gate_pi.stop()
        except Exception:
            pass
        pinion.shutdown()
        super().destroy_node()

def main():
    rclpy.init()
    node = ArucoTFListener()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()