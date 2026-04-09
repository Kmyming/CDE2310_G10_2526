#!/usr/bin/env python3

import time

import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool, String


class ShooterController(Node):
    def __init__(self):
        super().__init__('shooter_controller')

        # Safety-first defaults for Gazebo/subsystem tests.
        self.declare_parameter('enable_hardware', False)
        self.declare_parameter('simulated_shot_delay_sec', 1.5)
        self.declare_parameter('gate_pin', 17)
        self.declare_parameter('rack_pin', 27)
        self.declare_parameter('gate_delay_sec', 0.5)
        self.declare_parameter('rack_delay_sec', 0.3)

        self.enable_hardware = bool(self.get_parameter('enable_hardware').value)
        self.simulated_shot_delay_sec = float(self.get_parameter('simulated_shot_delay_sec').value)
        self.gate_pin = int(self.get_parameter('gate_pin').value)
        self.rack_pin = int(self.get_parameter('rack_pin').value)
        self.gate_delay = float(self.get_parameter('gate_delay_sec').value)
        self.rack_delay = float(self.get_parameter('rack_delay_sec').value)

        self.done_pub = self.create_publisher(Bool, '/shoot_done', 10)
        self.create_subscription(String, '/shoot_type', self.trigger_callback, 10)

        self._busy = False
        self._gpio_ready = False
        self._gpio = None
        self._servo_pwm = None

        if self.enable_hardware:
            self._init_gpio()
        else:
            self.get_logger().warn('Shooter hardware disabled. Running in simulated mode.')

    def _init_gpio(self):
        try:
            import RPi.GPIO as GPIO  # pylint: disable=import-outside-toplevel

            self._gpio = GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.rack_pin, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(self.gate_pin, GPIO.OUT)

            self._servo_pwm = GPIO.PWM(self.gate_pin, 50)
            self._servo_pwm.start(2.5)
            self._gpio_ready = True
            self.get_logger().info('Shooter GPIO initialized.')
        except Exception as exc:
            self.enable_hardware = False
            self._gpio_ready = False
            self.get_logger().error(f'Failed to initialize GPIO, falling back to simulated mode: {exc}')

    def trigger_callback(self, msg: String):
        if self._busy:
            return

        self._busy = True
        shoot_type = (msg.data or 'auto').strip().lower()

        try:
            if self.enable_hardware and self._gpio_ready:
                # Keep latest behavior simple and deterministic for LAUNCH state.
                if shoot_type == 'dynamic':
                    count = 3
                elif shoot_type == 'bonus':
                    count = 3
                else:
                    count = 3

                for _ in range(count):
                    self._shoot_once_hardware()
            else:
                time.sleep(self.simulated_shot_delay_sec)

            self.done_pub.publish(Bool(data=True))
            self.get_logger().info(f'Shooter cycle complete (type={shoot_type}), published /shoot_done=True')
        except Exception as exc:
            self.get_logger().error(f'Shooter cycle failed: {exc}')
            self.done_pub.publish(Bool(data=False))
        finally:
            self._busy = False

    def _shoot_once_hardware(self):
        self._set_servo_angle(90)
        time.sleep(self.gate_delay)
        self._set_servo_angle(0)

        self._gpio.output(self.rack_pin, self._gpio.HIGH)
        time.sleep(self.rack_delay)
        self._gpio.output(self.rack_pin, self._gpio.LOW)

    def _set_servo_angle(self, angle):
        angle = max(0, min(180, angle))
        duty_cycle = (angle / 18.0) + 2.5
        self._servo_pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)
        self._servo_pwm.ChangeDutyCycle(2.5)

    def destroy_node(self):
        if self._servo_pwm is not None:
            try:
                self._servo_pwm.stop()
            except Exception:
                pass

        if self._gpio is not None:
            try:
                self._gpio.cleanup()
            except Exception:
                pass

        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ShooterController()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
