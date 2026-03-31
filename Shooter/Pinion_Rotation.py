# MG90S 360° Continuous Rotation - Rack & Pinion Control
# Raspberry Pi 4B with RPi.GPIO
#
# MECHANISM:
#   Phase 1: Rotate 170° clockwise at full speed  (teeth engage rack)
#   Phase 2: Stop and hold position for HOLD_DURATION seconds
#   Phase 3: Rotate 360° more clockwise           (teeth disengage)
#   Phase 4: Stop, pause, repeat next cycle
#
# ⚠️  Angle control is TIME-BASED (no encoder feedback)
#     Calibrate SECONDS_PER_DEGREE for your specific servo before use!
#
# Wiring:
#   Orange = GPIO13 (Pin 33), Red = OpenCR 5V, Brown = OpenCR GND

import RPi.GPIO as GPIO
import time

# ---------------------------------------------------------
# USER PARAMETERS — edit these for your application
# ---------------------------------------------------------
HOLD_DURATION   = 5.0     # seconds: how long to hold after 170° rotation
CYCLE_PAUSE     = 2.0     # seconds: pause between cycles (0 = no pause)
NUM_CYCLES      = 3       # how many cycles to run (0 = infinite)
# ---------------------------------------------------------

# --- Servo Configuration ---
SERVO_PIN    = 13         # GPIO13 (Physical Pin 33)
PWM_FREQ     = 50         # 50Hz standard for servos

# --- Duty Cycle values ---
# Formula: (pulse_us / 20000us) × 100
# 1500µs → (1500/20000) × 100 = 7.5%  → STOP
# 2000µs → (2000/20000) × 100 = 10.0% → FULL SPEED CW
STOP_DUTY     = 7.5       # 1500µs — servo stops
FORWARD_DUTY  = 8      # 2000µs — full speed clockwise

# --- Fixed rotation angles ---
PHASE1_DEGREES = 170      # Phase 1: engage rack
PHASE3_DEGREES = 360      # Phase 3: disengage rack

# --- Time-based angle calculation ---
# At 120 RPM: 1 full rotation = 0.5 seconds
# Measure your actual servo and update SECONDS_PER_REV if needed
RPM                = 120
SECONDS_PER_REV    = 60.0 / RPM               # = 0.5 seconds
SECONDS_PER_DEGREE = SECONDS_PER_REV / 360.0  # = 0.001389 seconds/degree

def degrees_to_time(degrees):
    """Convert degrees of rotation to time in seconds."""
    return degrees * SECONDS_PER_DEGREE

# --- GPIO Setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, PWM_FREQ)
pwm.start(STOP_DUTY)      # always start in STOP state
time.sleep(0.5)            # let servo settle before first command

# --- Motor Control Functions ---

def forward():
    """Rotate clockwise at full speed."""
    pwm.ChangeDutyCycle(FORWARD_DUTY)

def stop_motor():
    """Stop the servo. 1500µs = 7.5% duty cycle."""
    pwm.ChangeDutyCycle(STOP_DUTY)

def rotate_degrees(degrees, label=""):
    """
    Rotate servo by a given number of degrees using time-based control.
    Then stops the servo.
    """
    duration = degrees_to_time(degrees)
    print(f"  Rotating {degrees}° ({label}) → duration: {duration:.4f}s")
    forward()
    time.sleep(duration)
    stop_motor()

def cleanup():
    """Always called on exit — stops servo and releases GPIO."""
    stop_motor()
    time.sleep(0.3)
    pwm.stop()
    GPIO.cleanup()
    print("GPIO cleaned up.")

# --- Single Cycle ---

def run_cycle(cycle_num):
    print(f"\n========== CYCLE {cycle_num} ==========")

    # --- Phase 1: Rotate 170° clockwise (teeth engage rack) ---
    print(f"[Phase 1] Rotating 170° CW — teeth engaging rack")
    rotate_degrees(PHASE1_DEGREES, label="engaging rack")

    # --- Phase 2: Hold position for HOLD_DURATION ---
    print(f"[Phase 2] Holding position for {HOLD_DURATION}s")
    time.sleep(HOLD_DURATION)

    # --- Phase 3: Rotate 360° more clockwise (teeth disengage) ---
    print(f"[Phase 3] Rotating 360° CW — teeth disengaging rack")
    rotate_degrees(PHASE3_DEGREES, label="disengaging rack")

    # --- Phase 4: Pause before next cycle ---
    print(f"[Phase 4] Cycle {cycle_num} complete. Waiting {CYCLE_PAUSE}s")
    time.sleep(CYCLE_PAUSE)

# --- Main ---

if __name__ == "__main__":
    print("=== MG90S Rack & Pinion Controller ===")
    print(f"Phase 1       : 170° CW at full speed")
    print(f"Phase 2       : Hold for {HOLD_DURATION}s")
    print(f"Phase 3       : 360° CW at full speed")
    print(f"Seconds/degree: {SECONDS_PER_DEGREE:.6f}s")
    print(f"Cycles        : {'Infinite' if NUM_CYCLES == 0 else NUM_CYCLES}")

    # try:
    #     if NUM_CYCLES == 0:
    #         cycle = 1
    #         while True:
    #             run_cycle(cycle)
    #             cycle += 1
    #     else:
    #         for cycle in range(1, NUM_CYCLES + 1):
    run_cycle(cycle)

    #     print("\nAll cycles complete.")
    #     stop_motor()

    # except KeyboardInterrupt:
    #     print("\nStopped by user (Ctrl+C)")
    stop_motor()
    # finally:
    cleanup()