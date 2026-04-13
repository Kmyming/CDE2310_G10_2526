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
HOLD_DURATION   = 1     # seconds
CYCLE_PAUSE     = 1    # seconds

# Engagement profile: mild | medium | strong
# Slower engage improves tooth catch. Disengage remains unchanged.
ENGAGE_PROFILE = "medium"

# --- Servo Configuration ---
SERVO_PIN    = 13         # GPIO13
# pigpio uses microseconds (us) directly for set_servo_pulsewidth
# 1500us is the neutral position for most servos
STOP_US      = 1500       
DISENGAGE_US = 1000       # Keep disengagement speed as current baseline

# Baseline timings from current validated behavior
ENGAGE_TIME_BASE_S = 0.40
DISENGAGE_TIME_S = 0.24

# Mild/medium/strong engage presets
ENGAGE_PRESETS = {
    "mild":   {"engage_us": 1000, "engage_time_s": 0.40},
    "medium": {"engage_us": 1200, "engage_time_s": 0.68},
    "strong": {"engage_us": 1300, "engage_time_s": 1.01},
}

# Per-cycle engage trim to reduce over-rotation on later cycles.
# cycle 1 uses no trim; cycle 2 subtracts one trim step, etc.
ENGAGE_TRIM_PER_EXTRA_CYCLE_S = 0.056
ENGAGE_TRIM_PER_EXTRA_CYCLE_S_2 = 0.064
ENGAGE_MIN_TIME_S = 0.25

# --- Fixed rotation angles ---
PHASE1_DEGREES = 180      
PHASE3_DEGREES = 360      

# --- GPIO Setup ---
pi = pigpio.pi()

if not pi.connected:
    print("CRITICAL: Could not connect to pigpiod. Run 'sudo pigpiod' in terminal first!")
    exit()

# Initialize in STOP state
pi.set_servo_pulsewidth(SERVO_PIN, STOP_US)
time.sleep(0.5)
print("PIGPIO connection established. Starting in STOP state.")
_shutdown_done = False


def get_engage_settings(profile_name):
    profile = str(profile_name).strip().lower()
    if profile not in ENGAGE_PRESETS:
        valid = ", ".join(sorted(ENGAGE_PRESETS.keys()))
        raise ValueError(f"Invalid ENGAGE_PROFILE '{profile_name}'. Choose one of: {valid}")
    return ENGAGE_PRESETS[profile]


ENGAGE_SETTINGS = get_engage_settings(ENGAGE_PROFILE)
ENGAGE_US = ENGAGE_SETTINGS["engage_us"]
ENGAGE_TIME_S = ENGAGE_SETTINGS["engage_time_s"]

# --- Motor Control Functions ---

def forward(pulse_us):
    """Rotate clockwise at full speed."""
    pi.set_servo_pulsewidth(SERVO_PIN, pulse_us)

def stop_motor():
    """Stop the servo using hardware-timed neutral pulse."""
    pi.set_servo_pulsewidth(SERVO_PIN, STOP_US)

def get_engage_time_for_cycle(cycle_index):
    cycle_index = max(0, int(cycle_index))
    if cycle_index <= 3:
        trimmed = ENGAGE_TIME_S - ENGAGE_TRIM_PER_EXTRA_CYCLE_S
    else:
        trimmed = ENGAGE_TIME_S - ENGAGE_TRIM_PER_EXTRA_CYCLE_S_2
    return max(ENGAGE_MIN_TIME_S, trimmed)


def rotate_degrees(degrees, label="", engage_time_s=None):
    """
    Rotate servo using calibrated phase timings.
    Engage timing comes from selected profile.
    Disengage timing remains fixed at DISENGAGE_TIME_S.
    """
    print(f"  Rotating {degrees}° ({label})")
    if label == "disengaging rack":
        forward(DISENGAGE_US)
        time.sleep(DISENGAGE_TIME_S)
    else:
        if engage_time_s is None:
            engage_time_s = ENGAGE_TIME_S
        forward(ENGAGE_US)
        time.sleep(engage_time_s)
    
    stop_motor()

def engage_rack(cycle_index=0):
    """Phase 1: engage teeth and pull rack back."""
    effective_engage_time = get_engage_time_for_cycle(cycle_index)
    print(
        f"[Pinion] Engage rack (engage_time={effective_engage_time:.3f}s, cycle={cycle_index + 1})"
    )
    rotate_degrees(PHASE1_DEGREES, label="engaging rack", engage_time_s=effective_engage_time)
    return effective_engage_time


def disengage_rack(cycle_index=0):
    """Phase 3: disengage teeth and release rack for launch."""
    print(f"[Pinion] Disengage rack (cycle={cycle_index + 1})")
    rotate_degrees(PHASE3_DEGREES, label="disengaging rack")


def shutdown():
    """Stops PWM signal and closes pigpio once at program end."""
    global _shutdown_done
    if _shutdown_done:
        return
    _shutdown_done = True
    stop_motor()
    time.sleep(0.1)
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.stop()
    print("PIGPIO connection closed.")

# --- Single Cycle ---

def run_cycle(cycle_index=0):
    engage_rack(cycle_index)

    # --- Phase 2: Hold position (Jitter-free hardware PWM) ---
    print(f"[Phase 2] Holding position for {HOLD_DURATION}s")
    time.sleep(HOLD_DURATION)

    # --- Phase 3: Disengage rack ---
    disengage_rack(cycle_index)

    # --- Phase 4: Pause ---
    print(f"[Phase 4] Cycle complete. Waiting {CYCLE_PAUSE}s")
    time.sleep(CYCLE_PAUSE)
    stop_motor()

# --- Main ---

if __name__ == "__main__":
    print("=== MG90S Rack & Pinion Controller (PIGPIO) ===")
    print(
        f"Profile={ENGAGE_PROFILE} | "
        f"ENGAGE_US={ENGAGE_US}, ENGAGE_TIME_S={ENGAGE_TIME_S} | "
        f"DISENGAGE_US={DISENGAGE_US}, DISENGAGE_TIME_S={DISENGAGE_TIME_S} | "
        f"ENGAGE_TRIM_PER_EXTRA_CYCLE_S={ENGAGE_TRIM_PER_EXTRA_CYCLE_S}"
    )

    run_cycle(0)
    shutdown()