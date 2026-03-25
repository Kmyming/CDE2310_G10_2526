#!/usr/bin/env python3

from turtle import delay

import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
import RPi.GPIO as GPIO
import time


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

        # optional storage for latest transform of each marker
        self.transforms_by_marker = {}

        self.get_logger().info(f"Subscribed to {self.topic}")

        # GPIO setup for Gates control
        GPIO.setmode(GPIO.BCM)
        self.gate = 17
        self.rack = 27
        GPIO.setup(self.gate, GPIO.OUT)
        GPIO.setup(self.rack, GPIO.OUT)
        self.gate_delay = 0.5
        self.rack_delay = 0.3

        self.dynamic_counter = 0 #Counter for dynamic delivery, to ensure we shoot only 3 times when the marker is in the correct position


    def cb(self, msg: TFMessage):
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

            elif marker_id == "10":
                self.dynamic_delivery(tf_data)

            elif marker_id == "21":
                self.status = "Engaged"
                self.bonus_delivery(tf_data)


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
        while time.time() - now < 1:
            pass

        # -------- Second Delivery --------
        now = time.time()
        self.shoot()
        while time.time() - now < delivery3_delay:
            pass
        
        # -------- Third Delivery --------
        self.shoot()

        

    def dynamic_delivery(self, tf_data):
        while self.dynamic_counter < 3:
            if tf_data["tx"] < 0.5 and tf_data["tx"] > -0.5:
                self.shoot()
                self.dynamic_counter += 1



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



    def shoot(self):
        GPIO.output(self.gate, GPIO.HIGH)  # Open Gate
        time.sleep(self.gate_delay)
        GPIO.output(self.gate, GPIO.LOW)   # Close Gate
        GPIO.output(self.rack, GPIO.HIGH)  # Push Rack
        time.sleep(self.rack_delay)
        GPIO.output(self.rack, GPIO.LOW)   # Pull Rack

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