---
title: Software Subsystem: Navigation and FSM
description: Frontier exploration, path planning, and mission state-machine design.
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

# Software Subsystem: Navigation and FSM

## Purpose

Provide autonomous frontier-based exploration, mission-state coordination, and velocity control for the TurtleBot3 mission stack.

## Runtime Entry Point

Navigation is launched from `remote_laptop_src/launch/nav_bringup.py` either directly or through the integrated bringup.

FSM logic is launched from `remote_laptop_src/launch/global_controller_bringup.py` through `mission_controller`.

## Launch Interface

- `enable_slam`
- `enable_rviz`
- `slam_params_file`
- `slam_start_delay_sec`
- `rviz_start_delay_sec`

## Exploration Algorithm

- Frontier detection identifies unexplored boundaries.
- Selected goals are forwarded to the motion stack.
- The controller advances until no frontiers remain.

## Path Planning

- The controller consumes map, odometry, and scan inputs.
- Waypoints are smoothed and followed using the configured controller behavior.

## Control Loop

- A timer-driven loop keeps navigation responsive.
- Delayed bringup helps avoid early TF and scan startup races.

## Parameters and Tuning

- `speed`
- `lookahead_distance`
- `expansion_size`
- `target_error`
- `robot_r`

## Launch Sequence

1. Source the workspace.
2. Start navigation bringup.
3. Confirm `/map`, `/odom`, and `/scan` are available.

## Failure Handling

- If the map is not available, the controller waits for SLAM.
- If the path is blocked, the controller should reselect a frontier or terminate cleanly.

## FSM Section

### Purpose

The finite state machine coordinates mission progression and subsystem handoff (explore, dock, launch, and completion).

### State flow

`EXPLORE -> DOCK -> LAUNCH -> EXPLORE -> END`

### Core FSM interfaces

- Subscribes to marker and completion signals.
- Publishes mission state updates on `/states`.
- Publishes shooter trigger mode on `/shoot_type`.

### Launch controls

- `enable_fsm` gates mission-controller startup.
- `enable_docking` and `enable_shooter` gate downstream behavior.

### FSM verification checks

```bash
ros2 topic echo /states
ros2 topic echo /shoot_type
```

Expected behavior:

- Initial state publishes `EXPLORE`.
- Transition events publish the next expected state without spurious loops.
