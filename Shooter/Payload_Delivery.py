#!/usr/bin/env python3

from turtle import delay

import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
from std_msgs.msg import Bool
import RPi.GPIO as GPIO
import time
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

        # GPIO setup for Gates control
        GPIO.setmode(GPIO.BCM)
        self.gate = 12
        GPIO.setup(self.gate, GPIO.OUT)
        self.gate_delay = 0.5
        self.rack_delay = 0.3
        self.p = GPIO.PWM(self.gate, 50)
        self.p.start(2.5) #start at 0 degrees
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
                self.status = "Engaged"
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
        while self.dynamic_counter < 3:
            if tf_data["tx"] < 0.5 and tf_data["tx"] > -0.5:
                self.shoot()
                self.dynamic_counter += 1

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



    def shoot(self):
        self.set_servo_angle(90)  # Open Gate
        time.sleep(self.gate_delay)
        self.set_servo_angle(0)   # Close Gate
        GPIO.cleanup()  # Clean up GPIO before using pigpio
        # Use the pinion rotation controller to cycle the rack/pinion
        try:
            pinion.run_cycle(0)
        except Exception as e:
            # Fallback to GPIO toggle if pigpio/pinion fails
            self.get_logger().error(f"Pinion run_cycle failed: {e}. Falling back to GPIO toggle")
    
    def set_servo_angle(self, angle):
        """
        Calculates duty cycle for specific angle and stops PWM to prevent jitter.
        Logic based on CDE2310 course provided material.
        """
        if angle < 0: angle = 0
        elif angle > 180: angle = 180

        duty_cycle = (angle / 18.0) + 2.5
        self.p.ChangeDutyCycle(duty_cycle)
        
        # Allow time for mechanical arm to move
        time.sleep(1)
        
        # SET TO 2.5 TO STOP JITTER: This kills the signal so the servo stays still
        self.p.ChangeDutyCycle(2.5)

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