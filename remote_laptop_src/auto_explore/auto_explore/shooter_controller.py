#!/usr/bin/env python3

import threading
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
        self.declare_parameter('pigpiod_host', 'localhost')
        self.declare_parameter('pigpiod_port', 8888)
        self.declare_parameter('gate_pin', 12)
        self.declare_parameter('rack_pin', 13)
        self.declare_parameter('ultrasonic_trigger_pin', 23)
        self.declare_parameter('ultrasonic_echo_pin', 24)
        self.declare_parameter('ultrasonic_distance_threshold_m', 0.70)
        self.declare_parameter('ultrasonic_simulated_distance_m', 0.15)
        self.declare_parameter('gate_open_us', 500)
        self.declare_parameter('gate_close_us', 1500)
        self.declare_parameter('gate_settle_s', 0.25)
        self.declare_parameter('engage_to_gate_open_offset_s', 0.0)
        self.declare_parameter('ball_drop_s', 0.25)
        self.declare_parameter('close_to_release_s', 0.08)
        self.declare_parameter('engage_profile', 'medium')
        self.declare_parameter('engage_trim_per_extra_cycle_s', 0.056)
        self.declare_parameter('engage_trim_per_extra_cycle_high_s', 0.064)
        self.declare_parameter('rack_hold_duration_s', 1.0)
        self.declare_parameter('rack_cycle_pause_s', 1.0)
        self.declare_parameter('dynamic_poll_interval_s', 0.05)
        self.declare_parameter('ultrasonic_echo_timeout_s', 0.03)
        self.declare_parameter('ultrasonic_poll_sleep_s', 0.0005)

        self.enable_hardware = bool(self.get_parameter('enable_hardware').value)
        self.simulated_shot_delay_sec = float(self.get_parameter('simulated_shot_delay_sec').value)
        self.pigpiod_host = str(self.get_parameter('pigpiod_host').value).strip()
        self.pigpiod_port = int(self.get_parameter('pigpiod_port').value)
        self.gate_pin = int(self.get_parameter('gate_pin').value)
        self.rack_pin = int(self.get_parameter('rack_pin').value)
        self.ultrasonic_trigger_pin = int(self.get_parameter('ultrasonic_trigger_pin').value)
        self.ultrasonic_echo_pin = int(self.get_parameter('ultrasonic_echo_pin').value)
        self.ultrasonic_distance_threshold_m = float(self.get_parameter('ultrasonic_distance_threshold_m').value)
        self.ultrasonic_simulated_distance_m = float(self.get_parameter('ultrasonic_simulated_distance_m').value)
        self.gate_open_us = int(self.get_parameter('gate_open_us').value)
        self.gate_close_us = int(self.get_parameter('gate_close_us').value)
        self.gate_settle_s = float(self.get_parameter('gate_settle_s').value)
        self.engage_to_gate_open_offset_s = float(self.get_parameter('engage_to_gate_open_offset_s').value)
        self.ball_drop_s = float(self.get_parameter('ball_drop_s').value)
        self.close_to_release_s = float(self.get_parameter('close_to_release_s').value)
        self.engage_profile = str(self.get_parameter('engage_profile').value).strip().lower()
        self.engage_trim_per_extra_cycle_s = float(self.get_parameter('engage_trim_per_extra_cycle_s').value)
        self.engage_trim_per_extra_cycle_high_s = float(self.get_parameter('engage_trim_per_extra_cycle_high_s').value)
        self.rack_hold_duration_s = float(self.get_parameter('rack_hold_duration_s').value)
        self.rack_cycle_pause_s = float(self.get_parameter('rack_cycle_pause_s').value)
        self.dynamic_poll_interval_s = float(self.get_parameter('dynamic_poll_interval_s').value)
        self.ultrasonic_echo_timeout_s = float(self.get_parameter('ultrasonic_echo_timeout_s').value)
        self.ultrasonic_poll_sleep_s = float(self.get_parameter('ultrasonic_poll_sleep_s').value)

        self._engage_profiles = {
            'mild': {'engage_us': 1000, 'engage_time_s': 0.40},
            'medium': {'engage_us': 1200, 'engage_time_s': 0.68},
            'strong': {'engage_us': 1300, 'engage_time_s': 1.01},
        }
        if self.engage_profile not in self._engage_profiles:
            self.get_logger().warn(
                f"Unknown engage_profile '{self.engage_profile}', falling back to 'medium'"
            )
            self.engage_profile = 'medium'

        self.done_pub = self.create_publisher(Bool, '/shoot_done', 10)
        self.create_subscription(String, '/shoot_type', self.trigger_callback, 10)

        self._lock = threading.Lock()
        self._busy = False
        self._pi = None
        self._pigpio_ready = False
        self._global_shot_count = 0

        if self.enable_hardware:
            self._init_pigpio()
        else:
            self.get_logger().warn('Shooter hardware disabled. Running in simulated mode.')

    def _init_pigpio(self):
        try:
            import pigpio  # pylint: disable=import-outside-toplevel

            self._pi = pigpio.pi(self.pigpiod_host, self.pigpiod_port)
            if not self._pi.connected:
                raise RuntimeError(f'Could not connect to pigpiod at {self.pigpiod_host}:{self.pigpiod_port}')

            self._pi.set_mode(self.gate_pin, pigpio.OUTPUT)
            self._pi.set_mode(self.rack_pin, pigpio.OUTPUT)
            self._pi.set_mode(self.ultrasonic_trigger_pin, pigpio.OUTPUT)
            self._pi.set_mode(self.ultrasonic_echo_pin, pigpio.INPUT)

            self._pi.write(self.ultrasonic_trigger_pin, 0)
            self._pi.set_servo_pulsewidth(self.gate_pin, self.gate_close_us)
            self._pi.set_servo_pulsewidth(self.rack_pin, 0)
            self._pigpio_ready = True
            self.get_logger().info('Shooter pigpio initialized.')
        except Exception as exc:
            self.enable_hardware = False
            self._pigpio_ready = False
            self.get_logger().error(f'Failed to initialize pigpio, falling back to simulated mode: {exc}')

    def trigger_callback(self, msg: String):
        shoot_type = (msg.data or 'auto').strip().lower()
        if shoot_type not in ('static', 'dynamic', 'bonus', 'auto'):
            shoot_type = 'auto'

        with self._lock:
            if self._busy:
                self.get_logger().warn('Shooter busy; ignoring trigger')
                return
            self._busy = True

        threading.Thread(target=self._run_delivery, args=(shoot_type,), daemon=True).start()

    def _run_delivery(self, shoot_type: str):
        success = True

        try:
            if self.enable_hardware and self._pigpio_ready:
                if shoot_type == 'static':
                    self._static_delivery()
                elif shoot_type == 'dynamic':
                    self._dynamic_delivery()
                elif shoot_type == 'bonus':
                    self._bonus_delivery()
                else:
                    self._static_delivery()
            else:
                # Sim mode keeps deterministic completion behavior for CI/Gazebo.
                time.sleep(self.simulated_shot_delay_sec)
        except Exception as exc:
            self.get_logger().error(f'Shooter cycle failed: {exc}')
            success = False
        finally:
            self.done_pub.publish(Bool(data=success))
            with self._lock:
                self._busy = False

            if success:
                self.get_logger().info(f'Shooter cycle complete (type={shoot_type}), published /shoot_done=True')

    def _static_delivery(self):
        delivery2_delay = 0.2
        delivery3_delay = 8.2

        self._shoot_once_hardware()
        time.sleep(delivery2_delay)

        self._shoot_once_hardware()
        time.sleep(delivery3_delay)

        self._shoot_once_hardware()

    def _dynamic_delivery(self):
        shot_count = 0
        while shot_count < 3:
            distance_m = self._read_ultrasonic_distance_m()
            if distance_m is not None and distance_m <= self.ultrasonic_distance_threshold_m:
                self._shoot_once_hardware()
                shot_count += 1
                continue

            time.sleep(self.dynamic_poll_interval_s)

    def _bonus_delivery(self):
        delivery_delay = 1.0

        for _ in range(3):
            self._shoot_once_hardware()
            time.sleep(delivery_delay)

    def _shoot_once_hardware(self):
        cycle_index = self._global_shot_count
        self.get_logger().info(f'Starting shot cycle {cycle_index + 1}')

        engage_thread = threading.Thread(target=self._engage_rack, args=(cycle_index,))
        offset = self.engage_to_gate_open_offset_s
        if offset >= 0.0:
            engage_thread.start()
            if offset > 0.0:
                time.sleep(offset)
            self._open_gate()
        else:
            self._open_gate()
            time.sleep(abs(offset))
            engage_thread.start()

        engage_thread.join()
        time.sleep(self.ball_drop_s)
        self._close_gate()
        time.sleep(self.close_to_release_s)

        self._disengage_rack(cycle_index)
        self._global_shot_count += 1

    def _get_engage_time_for_cycle(self, cycle_count: int) -> float:
        profile = self._engage_profiles.get(self.engage_profile, self._engage_profiles['medium'])
        base = profile['engage_time_s']
        cycle_count = max(0, int(cycle_count))
        if cycle_count <= 3:
            trimmed = base - self.engage_trim_per_extra_cycle_s
        else:
            trimmed = base - self.engage_trim_per_extra_cycle_high_s
        return profile['engage_us'], max(0.25, trimmed)

    def _engage_rack(self, cycle_count: int):
        engage_us, engage_time = self._get_engage_time_for_cycle(cycle_count)
        # Continuous servo pullback command.
        self._pi.set_servo_pulsewidth(self.rack_pin, engage_us)
        time.sleep(engage_time)
        self._pi.set_servo_pulsewidth(self.rack_pin, 1500)
        time.sleep(self.rack_hold_duration_s)

    def _disengage_rack(self, cycle_count: int):
        _ = cycle_count
        # Continuous servo release command.
        self._pi.set_servo_pulsewidth(self.rack_pin, 1000)
        time.sleep(self.rack_cycle_pause_s)
        self._pi.set_servo_pulsewidth(self.rack_pin, 1500)

    def _open_gate(self):
        self._pi.set_servo_pulsewidth(self.gate_pin, self.gate_open_us)
        time.sleep(self.gate_settle_s)

    def _close_gate(self):
        self._pi.set_servo_pulsewidth(self.gate_pin, self.gate_close_us)
        time.sleep(self.gate_settle_s)

    def _read_ultrasonic_distance_m(self):
        if not (self.enable_hardware and self._pigpio_ready):
            return self.ultrasonic_simulated_distance_m

        self._pi.gpio_trigger(self.ultrasonic_trigger_pin, 10, 1)
        read_start = time.monotonic()
        while self._pi.read(self.ultrasonic_echo_pin) == 0:
            if time.monotonic() - read_start > self.ultrasonic_echo_timeout_s:
                return None
            time.sleep(self.ultrasonic_poll_sleep_s)

        pulse_start = time.monotonic()

        while self._pi.read(self.ultrasonic_echo_pin) == 1:
            if time.monotonic() - pulse_start > self.ultrasonic_echo_timeout_s:
                return None
            time.sleep(self.ultrasonic_poll_sleep_s)

        pulse_end = time.monotonic()

        duration = pulse_end - pulse_start
        self.get_logger().info(f"Ultrasonic distance: {duration * 343.0 / 2.0:.2f} m")
        return (duration * 343.0) / 2.0

    def destroy_node(self):
        if self._pi is not None:
            try:
                self._pi.set_servo_pulsewidth(self.gate_pin, 0)
                self._pi.set_servo_pulsewidth(self.rack_pin, 0)
                self._pi.stop()
            except Exception:
                pass

        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ShooterController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
