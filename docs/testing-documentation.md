---
title: Testing Documentation
description: Subsystem, integration, and end-to-end validation.
---

# 🔗 Navigation

- [Home](index.md)
- [Requirements Specification](requirements-specification.md)
- [Concept of Operations](con-ops.md)
- [High Level Design](high-level-design.md)
- [Software Subsystem: Navigation and FSM](subsystem-nav-fsm.md)
- [Software Subsystem: ArUco Marker Detection](subsystem-software-aruco.md)
- [Mechanical Subsystem](subsystem-mechanical.md)
- [Electrical Subsystem](subsystem-electrical.md)
- [Interface Control Document](interface-control-document.md)
- [Software and Firmware Development](software-firmware-development.md)
- [Testing Documentation](testing-documentation.md)
- [User Manual](user-manual.md)
- [Areas for Improvement](improvements.md)
- [Appendix](appendix.md)

---

# Testing Documentation

## Test Strategy

- Validate each subsystem independently.
- Validate launch interface compatibility.
- Validate the integrated mission stack.

## Subsystem Tests

### 1) Package + launch interface sanity

```bash
ros2 pkg list | grep auto_explore
ros2 launch auto_explore global_bringup.py --show-args
ros2 pkg executables auto_explore
```

Expected: package is discoverable, launch arguments are listed, and executables include mission and controller nodes.

### 2) Navigation infrastructure (SLAM/RViz)

```bash
ros2 launch auto_explore nav_bringup.py use_sim_time:=true enable_slam:=true enable_rviz:=false
```

Check:

```bash
ros2 topic list | grep -E '^/map$|^/map_metadata$'
```

Expected: `/map` is available and updating.

### 3) FSM only

```bash
ros2 launch auto_explore global_controller_bringup.py use_sim_time:=true \
	enable_fsm:=true enable_navigation:=false enable_markers:=false \
	enable_docking:=false enable_shooter:=false
```

Check:

```bash
ros2 topic echo /states
```

Expected: FSM publishes `EXPLORE` on startup.

### 4) Exploration controller only

```bash
ros2 launch auto_explore global_controller_bringup.py use_sim_time:=true \
	enable_fsm:=false enable_navigation:=true enable_markers:=false \
	enable_docking:=false enable_shooter:=false
```

Check:

```bash
ros2 topic hz /cmd_vel
ros2 topic echo /map_explored
```

Expected: `/cmd_vel` publishes while navigating; `/map_explored` eventually becomes true.

#### Navigation Testing Results (Physical Maze)

**Test Environment:** TurtleBot 3 Burger in physical maze  
**ROS 2 Distro:** Humble  
**Test Date Range:** 27/03 - 31/03/2026  

##### Session S1 (27/03, 3:32 PM) – SLAM Dependency Issues

| Metric | Result |
|--------|--------|
| Outcome | **Fail** |
| Run Time | 0 min 0 s |
| Mapped Area | 0% |
| Collisions | 0 / 0 |

**Configuration:**
- `lookahead_distance:` 0.24 m
- `speed:` 0.18 m/s
- `expansion_size:` 3
- `target_error:` 0.15 m
- `robot_r:` 0.2 m

**Observations:**
- SLAM Toolbox had QoS dependency issues; could run in Gazebo but not with robot bringup
- Bot did not move as no SLAM map was created

**Evidence:**
- ![Test Environment S1](../testing-media/images/maze_environment_s1.jpg)

**Changes for Next Session:**
- Updated SLAM configuration in `/opt/ros/humble/share/slam_toolbox/config/mapper_params_online_async.yaml`

---

##### Session S2 (27/03, 4:04 PM) – First Movement & Collision

| Metric | Result |
|--------|--------|
| Outcome | **Partial** |
| Run Time | 0 min 26 s |
| Mapped Area | ~5% |
| Collisions | 1 |

**Configuration:**
- `lookahead_distance:` 0.24 m
- `speed:` 0.18 m/s
- `expansion_size:` 3
- `target_error:` 0.15 m
- `robot_r:` 0.2 m
- Updated SLAM mapper parameters: `map_update_interval: 1.0`, `min_laser_range: 0.12`, `max_laser_range: 3.5`, `minimum_travel_distance: 0.2`

**Observations:**
- Bot collided with wall after first turn
- Map generated but SLAM latency caused delayed obstacle awareness
- Robot did not avoid walls/obstacles effectively

**Evidence:**
- ![SLAM Map Generated S2](../testing-media/images/slam_map_s2.png)
- Video: [Collision Incident S2](../testing-media/videos/collision_s2.mp4)

**Changes for Next Session:**
- Reduce speed from 0.18 m/s to 0.09 m/s to counteract SLAM latency and enable smoother maneuvering

---

##### Session S3 (31/03, 3:27 PM) – Speed Reduction & Success

| Metric | Result |
|--------|--------|
| Outcome | **Success** ✓ |
| Run Time | 0 min 53 s |
| Mapped Area | 100% |
| Collisions | 0 / 0 |

**Configuration:**
- `lookahead_distance:` 0.24 m
- `speed:` 0.09 m/s *(reduced from 0.18)*
- `expansion_size:` 3
- `target_error:` 0.15 m
- `robot_r:` 0.2 m

**Procedure:**
- Max speed reduced from 0.18 m/s to 0.09 m/s to accommodate SLAM processing latency
- Robot allowed to explore maze autonomously without intervention

**Observations:**
- Robot successfully navigated entire maze without collision
- Reduced speed (0.09 m/s) provided sufficient time for SLAM to update map before path planning decisions
- Smooth exploration pattern with effective frontier detection
- No oscillation or navigation errors observed
- Complete map coverage achieved in under 1 minute
- Robot correctly transitioned to completion state upon 100% map coverage

**Evidence:**
- ![Test Setup S3](../testing-media/images/maze_setup_s3.jpg)
- Video: [Run Video S3](../testing-media/videos/exploration_run_s3.mp4)
- ![RViz Map S3](../testing-media/images/rviz_map_s3.png)

**Key Findings:**
- **Speed optimization is critical:** Reducing speed from 0.18 m/s to 0.09 m/s eliminated collisions
- **SLAM latency resolved:** Slower movement rate allowed map updates to propagate before path planning
- **Frontier algorithm effective:** Algorithm successfully identified and navigated to unexplored regions
- **Completion criteria met:** 100% map coverage achieved with zero collisions in 53 seconds

### 5) Marker detection only

```bash
ros2 launch auto_explore global_controller_bringup.py use_sim_time:=true \
	enable_fsm:=false enable_navigation:=false enable_markers:=true \
	enable_pose_publisher:=true enable_docking:=false enable_shooter:=false
```

Check:

```bash
ros2 topic echo /aruco/debug
ros2 topic echo /tf
ros2 topic echo /marker_detected
```

Expected: the ArUco detection node should publish heartbeat/debug output on `/aruco/debug`, publish `true` on `/marker_detected` when a marker is visible, and publish marker pose transforms on `/tf` with frame names of the form `aruco_marker_<id>`.

#### ArUco Marker Detection Testing Results (Physical Robot)

**Test Environment:** TurtleBot 3 Burger with Raspberry Pi camera and printed ArUco marker  
**ROS 2 Distro:** Humble  
**Test Date Range:** 02/04/2026  

##### Session A1 (02/04, 3:07 PM) – Heartbeat, Detection State, and Pose Publishing Validation

| Metric | Result |
|--------|--------|
| Outcome | **Success** ✓ |
| Run Time | 1 min 12 s |
| Marker IDs Detected | 1 |
| Detection State | **`true`** |

**Configuration:**
- `image_topic:` `/camera/image_raw`
- `camera_info_topic:` `/camera/camera_info`
- `camera_frame:` `camera_optical_frame`
- `marker_size_m:` 0.049 m
- `dictionary:` `DICT_4X4_250`
- Marker placement distance: ~0.35 m to 0.60 m from camera

**Procedure:**
- Launched the ArUco pose streamer independently with marker detection enabled
- Checked `/aruco/debug` to confirm heartbeat and debug JSON output
- Checked `/marker_detected` to confirm marker visibility state
- Checked `/tf` to confirm pose transform publishing for the detected marker

**Observations:**
- The subsystem worked correctly on the first physical test run without requiring code changes
- `/aruco/debug` published both heartbeat information and marker debug data as expected
- `/marker_detected` correctly changed to `true` when the marker entered the camera view
- `/tf` published the marker pose using parent frame `camera_optical_frame` and child frame `aruco_marker_<id>`
- The published pose output was stable enough to be used directly by the downstream docking subsystem

**Evidence:**
- Setup Image: [ArUco Detection Validation](../testing-media/videos/Aruco_Test_d1.jpg)
- Screenshot: [/marker_detected output](../testing-media/videos/Aruco_marker_detected.png)
- Screenshot: [/tf output](../testing-media/videos/Aruco_tf.png)
- Screenshot: [/arUco/debug output](../testing-media/videos/Aruco_aruco_debug.png)

**Key Findings:**
- **Heartbeat output worked correctly:** the node continuously indicated that the subsystem was running
- **Detection state publishing worked correctly:** marker visibility was reflected reliably on `/marker_detected`
- **Pose publishing worked correctly:** TF transforms were published in the expected frame structure for downstream use
- **Subsystem was ready for integration:** marker output was immediately usable by the docking controller

### 6) Docking controller only

```bash
ros2 launch auto_explore global_controller_bringup.py use_sim_time:=true \
	enable_fsm:=false enable_navigation:=false enable_markers:=false \
	enable_docking:=true enable_shooter:=false
```

Check:

```bash
ros2 topic info /cmd_vel_docking
ros2 topic info /dock_done
ros2 topic echo /docking_state
```

Expected: docking topics are present, the controller is alive, and the docking state machine publishes valid transitions during a run.

#### Docking Testing Results (Physical Robot)

**Test Environment:** TurtleBot 3 Burger with camera-based ArUco docking target  
**ROS 2 Distro:** Humble  
**Test Date Range:** 04/04 - 08/04/2026  

##### Session D1 (04/04, 5:10 PM) – Initial Path-Based Docking Attempt

| Metric | Result |
|--------|--------|
| Outcome | **Fail** |
| Run Time | 0 min 18 s |
| Dock Complete | No |
| Marker Lock | Intermittent |

**Configuration:**
- `lookahead_distance:` 0.24 m
- `cruise_speed:` 0.12 m/s
- `target_error:` 0.10 m
- `robot_safety_radius:` 0.20 m
- `final_align_trigger_margin:` 0.50 m
- `max_path_ang_speed:` 0.70 rad/s
- `max_final_ang_speed:` 0.15 rad/s
- Marker set tested: `0, 10, 21, 30, 31, 32`

**Procedure:**
- Ran the earlier docking controller version that combined A* planning, B-spline smoothing, path following, search rotation, and TF-based final alignment
- Tested on the physical robot with real `/tf`, `/odom`, `/scan`, and `/map` inputs

**Observations:**
- Controller logic performed correctly in Gazebo but was not reliable on the real robot
- In physical testing, the robot either remained stationary or just rotated side to side during docking attempts
- Marker-triggered phase transitions occurred, but the global behaviour was not stable enough for successful docking
- This suggested a gap between simulated frame assumptions and real-world robot behaviour

**Evidence:**
- Video: [Physical Docking Failure D1](../testing-media/videos/docking_failure_d1.mp4)

**Changes for Next Session:**
- Replaced the path-heavy docking approach with a simpler state-based controller using direct pose feedback from ArUco and a LiDAR verification check in the final approach stage

---

##### Session D2 (06/04, 4:42 PM) – Pose-Based Docking Controller Success

| Metric | Result |
|--------|--------|
| Outcome | **Success** ✓ |
| Run Time | 0 min 21 s |
| Dock Complete | Yes |
| Marker Lock | Stable |

**Configuration:**
- `forward_speed:` 0.08 m/s
- `turn_kp:` 1.8
- `max_ang_speed:` 0.25 rad/s
- `turn_tolerance:` 2.0 deg
- `mid_tz_threshold:` 0.30 m
- `final_tz_threshold:` 0.10 m
- `tx_align_tolerance:` 0.01 m
- `tx_final_align_tolerance:` 0.05 m
- Added docking fail-safes: `marker_invisible_timeout_sec: 30.0`, `state_timeout_sec: 45.0`

**Procedure:**
- Re-tested using the revised docking controller based on a staged state machine:
  `SEARCH -> APPROACH_1 -> TURN_SIDE / DRIVE_SIDE -> TURN_FACE_MARKER -> FINAL_APPROACH -> DONE`
- Used ArUco pose data for alignment and LiDAR as a final safety confirmation near the docking threshold

**Observations:**
- Robot successfully rotated to face the marker, approached it, corrected its heading, and completed final docking
- State transitions were consistent and easier to debug than in the earlier controller version
- The simplified approach reduced incorrect path behaviour seen in D1
- LiDAR provided a useful final cross-check before declaring docking complete
- `/dock_done` published the expected completion signal at the end of the sequence

**Evidence:**
- Video: [Docking Run Video 1 D2](../testing-media/videos/docking_success_d2_1.mp4)
- Video: [Docking Run Video 2 D2](../testing-media/videos/docking_success_d2_2.mp4)

**Key Findings:**
- **Simpler control logic was more robust:** direct pose-based alignment outperformed the earlier planner-heavy implementation on hardware
- **State-machine visibility improved debugging:** the explicit docking states made it easier to identify where errors occurred
- **Final sensing redundancy helped:** LiDAR confirmation reduced the chance of false completion near the target
- **Physical docking criteria were met:** the robot completed docking reliably within the acceptable stopping distance

---

### 7) Shooter controller only

Simulation-safe launch:

```bash
ros2 launch auto_explore global_controller_bringup.py use_sim_time:=true \
	enable_fsm:=false enable_navigation:=false enable_markers:=false \
	enable_docking:=false enable_shooter:=true shooter_enable_hardware:=false
```

Trigger shooter modes:

```bash
ros2 topic pub --once /shoot_type std_msgs/String "data: static"
ros2 topic pub --once /shoot_type std_msgs/String "data: dynamic"
```

Expected: shooter starts without GPIO access errors.

## Integration Tests

### Navigation + Mission Control

**Test Status:** In progress (pending S3 results)  

**Test Objective:** Verify frontier-based exploration integrates correctly with FSM state machine.

**Procedure:**
```bash
ros2 launch auto_explore global_controller_bringup.py use_sim_time:=false \
	enable_fsm:=true enable_navigation:=true enable_markers:=false \
	enable_docking:=false enable_shooter:=false
```

**Evidence Placeholder:**
- Video: [FSM State Transitions](../testing-media/videos/fsm_state_transitions_nav.mp4)
- ![Navigation Integrated Output](../testing-media/images/integration_test_nav.jpg)

### Marker Detection + Mission Control

**Test Objective:** Verify that FSM-controlled mission flow can transition into marker-aware behavior once a marker becomes visible.

**Procedure:**
```bash
ros2 launch auto_explore global_controller_bringup.py use_sim_time:=false \
	enable_fsm:=true enable_navigation:=false enable_markers:=true \
	enable_pose_publisher:=true enable_docking:=false enable_shooter:=false
```

**Expected Behavior:**
- FSM remains alive while marker topics are active
- Marker detection continues publishing independently of navigation
- Visible marker data is available for downstream docking logic

**Evidence Placeholder:**
- Video: [FSM + Marker Detection](../testing-media/videos/fsm_marker_integration.mp4)

### Full Bringup with Toggles Enabled

**Test Objective:** Verify that navigation, FSM, marker detection, and docking interfaces can coexist without launch conflicts.

**Procedure:**
```bash
ros2 launch auto_explore global_bringup.py \
	use_sim_time:=false enable_slam:=false enable_rviz:=false \
	enable_fsm:=true enable_navigation:=true enable_markers:=true \
	enable_pose_publisher:=true enable_docking:=true enable_shooter:=false
```

**Expected Behavior:**
- All required nodes launch without runtime exceptions
- Core topics remain available simultaneously
- Marker and docking interfaces do not break navigation bringup

**Evidence Placeholder:**
- Screenshot: `ros2 node list`
- Screenshot: `ros2 topic list`

## End-to-End Mission Tests

### Full smoke test (simulation)

```bash
ros2 launch auto_explore global_bringup.py \
	use_sim_time:=true enable_slam:=true enable_rviz:=false \
	enable_fsm:=true enable_navigation:=true enable_markers:=true \
	enable_pose_publisher:=true enable_docking:=false enable_shooter:=false
```

Check:

```bash
ros2 topic list | grep -E '^/states$|^/aruco/debug$|^/cmd_vel$|^/map$|^/odom$'
```

Expected: critical topics are present and active.

### Full stack test (real robot)

Run robot bringup and launch integrated mission stack with real-time settings and hardware flags.

## Acceptance Criteria

- Required topics appear.
- Nodes launch without runtime exceptions.
- Mission states transition as expected.

## Navigation Subsystem Summary

**Subsystem Owner:** Navigation / Autonomous Exploration  
**Test Period:** 27/03/2026 – 31/03/2026  
**Physical Environment:** Maze with walls and tight passages  

### Test Results Summary

| Session | Date | Outcome | Key Issue | Speed | Mapped % | Collisions |
|---------|------|---------|-----------|-------|----------|------------|
| S1 | 27/03 | Fail | SLAM config error | 0.18 | 0% | 0 |
| S2 | 27/03 | Partial | Wall collision | 0.18 | 5% | 1 |
| S3 | 31/03 | **Success** | Speed optimization | 0.09 | **100%** | **0** |

### Key Learnings

1. **SLAM Latency:** Critical factor affecting real-time obstacle avoidance
2. **Speed Sensitivity:** Higher speeds (0.18 m/s) exceeded SLAM update rate; slower speeds (0.09 m/s) recommended
3. **Mapper Parameters:** Fine-tuning `map_update_interval`, `minimum_travel_distance`, and laser range bounds essential for responsiveness
4. **Frontier Algorithm:** Core algorithm functional; primary issue is external timing constraints rather than algorithmic failure

### Recommendations

- S3 parameters (speed: 0.09 m/s) are recommended for operational deployment
- Current configuration successfully meets acceptance criteria: 100% map coverage with 0 collisions
- Further optimization may focus on reducing exploration time without sacrificing safety
- Consider implementing dynamic speed scaling based on map confidence for future enhancements


## ArUco Marker Detection Subsystem Summary

**Subsystem Owner:** Perception / Marker Detection  
**Test Period:** 02/04/2026  
**Physical Environment:** Indoor bench and floor-level marker visibility tests  

### Test Results Summary

| Session | Date | Outcome | Key Issue | TF Output | Detection State |
|---------|------|---------|-----------|-----------|-----------------|
| A1 | 02/04 | **Success** | First-run validation | **Published** | **`true`** |

### Key Learnings

1. **Heartbeat output was verified:** the subsystem continuously indicated that the node was running
2. **Marker visibility publishing was correct:** `/marker_detected` reflected marker presence correctly
3. **Pose publishing was successful:** TF transforms were published correctly for the visible marker
4. **Subsystem worked first shot:** no code changes were required before integration with docking

### Recommendations

- Keep the same camera topic and marker size configuration for integration testing
- Record topic screenshots for `/aruco/debug`, `/tf`, and `/marker_detected` during demonstrations
- Maintain a clear frontal view of the marker for best pose stability

## Docking Subsystem Summary

**Subsystem Owner:** Docking / Final Alignment Control  
**Test Period:** 04/04/2026 – 08/04/2026  
**Physical Environment:** Indoor floor docking tests using ArUco-based visual docking target  

### Test Results Summary

| Session | Date | Outcome | Key Issue | Dock Complete | Notes |
|---------|------|---------|-----------|---------------|-------|
| D1 | 04/04 | Fail | Planner-heavy controller unstable on hardware | No | Worked in Gazebo, not on robot |
| D2 | 06/04 | **Success** | Simplified control logic | **Yes** | Full docking completed |


### Key Learnings

1. **Hardware realism matters:** a controller that appears correct in Gazebo may still fail on the physical platform
2. **Simpler docking logic was more effective:** direct pose-based control using ArUco measurements was more reliable than the earlier path-planning approach
3. **State-machine structure improved reliability:** explicit state transitions made debugging, testing, and recovery much easier
4. **Sensor redundancy improved confidence:** ArUco pose guidance combined with LiDAR confirmation produced a more dependable final approach

### Recommendations

- Use the revised pose-based controller as the baseline docking implementation
- Keep the successful D2 parameter set for demonstrations and integration testing
- Preserve watchdog-based abort logic in all future docking revisions
- During demonstrations, record both the robot motion and topic output for stronger validation evidence

## Known Test Gaps

- Long-duration exploration runs (>5 min) not yet validated
- Integration with full mission FSM (marker detection + docking) pending
- Hardware-specific validation remains dependent on available robot access

## Evidence and Results

- Suggested evidence artifacts:
	- topic snapshots (`ros2 topic list`, `ros2 topic hz`)
	- node lists (`ros2 node list`)
	- launch logs from `~/.ros/log/`
	- RViz screenshots or short run recordings
   
# Testing Documentation: Electrical Subsystem

## Test Strategy

- **Unit Validation**: Confirm individual component functionality (Servos, Ultrasonic) before full integration.
- **Signal Integrity**: Verify logic level compatibility between the Raspberry Pi and actuators.
- **Power Reliability**: Ensure the power distribution network handles currents without system brownouts.
- **Mission Endurance**: Validate the 25-minute operational requirement under real-world conditions.

## Subsystem Unit Tests

### 1) MG90S PWM Logic Level Test

**Objective**: Verify MG90S response to different control voltages.

**Procedure**: Initially connected MG90S directly to RPi GPIO 13. Following failure, integrated BOB-11978 Level Shifter. Verified signal using a Digital Multimeter.

**Observations**:
- At 3.3V PWM: The servo remained still and failed to actuate.
- At 5.0V PWM (via BOB-11978): Servo responded correctly to PWM commands.

**Result**: ✅ Success (Requires Level Shifter)

---

### 2) HC-SR04 Voltage Divider Safety

**Objective**: Protect RPi GPIO from 5V Echo signals.

**Procedure**: Implemented 1kΩ-2kΩ voltage divider. Measured output voltage with a Digital Multimeter during active ranging.

- **Expected**: Signal stepped down to ~3.3V.
- **Actual**: ~3.33V measured at GPIO 24.

**Result**: ✅ Success

---

### 3) Startup Stability Test

**Objective**: Ensure "No unintended actuation of servos or drive motors on startup" (Req 2.4).

**Procedure**: Monitored SG90 and MG90S positions during OpenCR and RPi boot cycles.

**Observations**: Both servos successfully initialized to stop/closed pulse widths without jitter or movement before commands were issued.

**Result**: ✅ Success

---

### 4) Full Endurance Run (Physical)

**Test Environment:** NUS IDP Studio 2  
**Test Date:** 13/04/2026 – 16/04/2026  
**Robot State:** Integrated launcher mechanism and navigation stack active.

| Metric | Target | Result |
|--------|--------|--------|
| Outcome | Success | Mission Completed |
| Run Time | 25 min 0 s | 25 min 0 s |
| Battery Voltage | >11 V | >11 V (Alarm stayed silent) |

**Observations**:
- Robot completed the full duration without triggering the OpenCR low-voltage alarm (threshold: 11V).
- Confirmed battery capacity remains sufficient for the 25-minute requirement, consistent with the predicted worst-case runtime of 54.9 minutes.
- No system brownouts or reboots occurred during concurrent movement and servo actuation.
