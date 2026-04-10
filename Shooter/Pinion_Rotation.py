# MG90S 360° Continuous Rotation - Rack & Pinion Control
# Raspberry Pi 4B with PIGPIO (Hardware PWM)
#
# Wiring:
#   Orange = GPIO13 (Pin 33), Red = OpenCR 5V, Brown = OpenCR GND

import pigpio
import time

# ---------------------------------------------------------
# USER PARAMETERS
# ---------------------------------------------------------
HOLD_DURATION   = 7     # seconds
CYCLE_PAUSE     = 5     # seconds

# --- Servo Configuration ---
SERVO_PIN    = 13         # GPIO13
# pigpio uses microseconds (us) directly for set_servo_pulsewidth
# 1500us is the neutral position for most servos
STOP_US      = 1500       
FORWARD_US   = 1000       # 1000us = Full speed clockwise

# --- Fixed rotation angles ---
PHASE1_DEGREES = 170      
PHASE3_DEGREES = 360      

# --- GPIO Setup ---
pi = pigpio.pi()

if not pi.connected:
    print("CRITICAL: Could not connect to pigpiod. Run 'sudo pigpiod' in terminal first!")
    exit()

# Initialize in STOP state
pi.set_servo_pulsewidth(SERVO_PIN, STOP_US)
time.sleep(0.5)

# --- Motor Control Functions ---

def forward():
    """Rotate clockwise at full speed."""
    pi.set_servo_pulsewidth(SERVO_PIN, FORWARD_US)

def stop_motor():
    """Stop the servo using hardware-timed neutral pulse."""
    pi.set_servo_pulsewidth(SERVO_PIN, STOP_US)

def rotate_degrees(degrees, label=""):
    """
    Rotate servo using your measured timings.
    Phase 1 (Engage): 0.581s
    Phase 3 (Disengage): 0.42s
    """
    print(f"  Rotating {degrees}° ({label})")
    forward()
    
    if label == "disengaging rack":
        time.sleep(0.35)
    else:
        # Phase 1: 170 degrees (engaging rack)
        time.sleep(0.44)
        
    stop_motor()

def cleanup():
    """Stops PWM signal entirely and closes connection."""
    stop_motor()
    time.sleep(0.3)
    pi.set_servo_pulsewidth(SERVO_PIN, 0) # Kill signal for safety
    pi.stop()
    print("PIGPIO connection closed.")

# --- Single Cycle ---

def run_cycle():
    # --- Phase 1: Engage rack ---
    print(f"[Phase 1] Rotating 170° CW — teeth engaging rack")
    rotate_degrees(PHASE1_DEGREES, label="engaging rack")

    # --- Phase 2: Hold position (Jitter-free hardware PWM) ---
    print(f"[Phase 2] Holding position for {HOLD_DURATION}s")
    time.sleep(HOLD_DURATION)

    # --- Phase 3: Disengage rack ---
    print(f"[Phase 3] Rotating back to normal position — teeth disengaging rack")
    rotate_degrees(PHASE3_DEGREES, label="disengaging rack")

    # --- Phase 4: Pause ---
    print(f"[Phase 4] Cycle complete. Waiting {CYCLE_PAUSE}s")
    time.sleep(CYCLE_PAUSE)

# --- Main ---

if __name__ == "__main__":
    print("=== MG90S Rack & Pinion Controller (PIGPIO) ===")
    
    # Run two cycles as per your original main logic
    run_cycle()
    run_cycle()

    stop_motor()
    cleanup()