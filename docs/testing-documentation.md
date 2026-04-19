---
title: Testing Documentation
description: Subsystem, integration, and end-to-end validation.
---

## 🔗 Navigation

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

### 5) Marker detection only

```bash
ros2 launch auto_explore global_controller_bringup.py use_sim_time:=true \
	enable_fsm:=false enable_navigation:=false enable_markers:=true \
	enable_pose_publisher:=true enable_docking:=false enable_shooter:=false
```

Check:

```bash
ros2 topic echo /aruco/debug
```

Expected: heartbeat JSON plus marker JSON when marker is in view.

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
```

Expected: docking topics are present and node is alive.

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

- Navigation + mission control.
- Marker detection + mission control.
- Full bringup with toggles enabled.

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

## Known Test Gaps

- Hardware-specific validation remains dependent on available robot access.

## Evidence and Results

- Suggested evidence artifacts:
	- topic snapshots (`ros2 topic list`, `ros2 topic hz`)
	- node lists (`ros2 node list`)
	- launch logs from `~/.ros/log/`
	- RViz screenshots or short run recordings
