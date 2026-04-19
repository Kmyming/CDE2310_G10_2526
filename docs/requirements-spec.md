---
title: Requirements Specification
description: Mission requirements, constraints, and traceability.
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

# Requirements Specification

## Problem Statement

The system must autonomously explore an unknown indoor warehouse-style arena, detect ArUco fiducial markers identifying two delivery receptacles, dock precisely in front of each receptacle, and deliver exactly three ping-pong balls per receptacle — all without manual teleoperation after mission start. One receptacle is static; the other moves laterally at an unknown speed, requiring sensor-gated delivery timing. The complete mission must be executed within a **25-minute window** on a TurtleBot3 Burger platform running ROS 2 Humble.

---

## Stakeholder Needs

- Autonomous exploration of a fully unknown maze environment with no prior map.
- Reliable detection and 6-DOF pose estimation of ArUco markers under realistic lighting and partial occlusion.
- Deterministic mission state transitions that handle both success and failure paths without operator input.
- Correct, sequenced ball delivery into both a static and a moving receptacle.
- Clear operator setup and shutdown procedures requiring minimal technical expertise.
- A single-command launch that brings up the full mission stack for both simulation and real hardware.

---

## Functional Requirements

### Navigation and Mapping

**FR-01** — The system shall autonomously build a 2D occupancy grid of the arena using LiDAR-based SLAM without any prior map data.

**FR-02** — The system shall implement frontier-based exploration to discover and navigate to unexplored regions of the map systematically, scoring frontiers by a ratio of frontier size to A\* path distance.

**FR-03** — The system shall plan collision-free paths to frontier targets using the A\* algorithm on the inflated costmap and track those paths using a pure-pursuit controller.

**FR-04** — The system shall apply local obstacle avoidance using segmented LiDAR scan sectors, overriding path-following commands when obstacles are detected within `robot_r` of the robot body.

**FR-05** — The system shall publish a `/map_explored` signal (`Bool`, `True`) when no valid frontier groups remain in the occupancy grid.

### Marker Detection

**FR-06** — The system shall detect ArUco markers (dictionary `DICT_4X4_250`) from the Raspberry Pi camera feed and estimate their 6-DOF pose (translation vector `tvec`, rotation vector `rvec`) using OpenCV's `estimatePoseSingleMarkers`.

**FR-07** — The system shall broadcast each detected marker's pose as a TF transform (`aruco_marker_<id>`) and publish a `/marker_detected` (`Bool`) signal when at least one marker is visible.

**FR-08** — The system shall identify the delivery zone type from the marker ID: marker ID `0` corresponds to the static receptacle zone; marker ID `1` corresponds to the dynamic receptacle zone.

**FR-09** — The system shall use a fallback pinhole camera model when valid intrinsics are not available from `/camera/camera_info`, logging a warning and continuing detection.

**FR-10** — The system shall suppress duplicate zone-detection signals: once a zone has been marked as visited by the FSM, further detections of that zone's marker shall be ignored.

### Mission State Machine

**FR-11** — The system shall implement a finite state machine (FSM) with the following top-level states: `EXPLORE`, `DOCK`, `LAUNCH`, `BACKUP`, and `END`.

**FR-12** — The FSM shall transition from `EXPLORE` to `DOCK` upon receiving a `/marker_detected = True` signal for an unvisited zone while in the `EXPLORE` state.

**FR-13** — The FSM shall transition from `DOCK` to `LAUNCH` upon receiving `/dock_done = True`, and return to `EXPLORE` upon receiving `/dock_done = False`.

**FR-14** — The FSM shall transition from `LAUNCH` to `BACKUP` after the shooter signals `/shoot_done = True` and a minimum hold duration of 15 seconds has elapsed.

**FR-15** — The FSM shall transition from `BACKUP` to `EXPLORE` after the robot has reversed for 2 seconds, clearing the delivery zone.

**FR-16** — The FSM shall transition to `END` when the map is fully explored and both delivery zones have been visited (`marker_count >= 2`).

**FR-17** — The FSM shall arbitrate velocity commands from the navigation controller (`/cmd_vel_nav`) and the docking controller (`/cmd_vel_docking`), publishing the active controller's output to `/cmd_vel` based on the current state.

### Docking

**FR-18** — The docking controller shall implement a multi-stage docking state machine with the states: `IDLE`, `SEARCH`, `APPROACH_1`, `TURN_SIDE`, `DRIVE_SIDE`, `TURN_FACE_MARKER`, `FINAL_APPROACH`, `DONE`, `ABORT`, `OBSTACLE_AVOIDANCE`, and `SPECIAL_SEARCH`.

**FR-19** — The docking controller shall rotate the robot until the marker's lateral offset `tx` is within ±0.01 m before beginning the approach.

**FR-20** — The docking controller shall compute a geometric perpendicular approach manoeuvre using the marker's pose angle `θ` when `tz < 0.30 m`, including a lateral drive step and a realignment turn.

**FR-21** — The docking controller shall terminate the final approach and publish `/dock_done = True` when `tz < 0.10 m` or the front LiDAR average reads below `0.20 m`.

**FR-22** — The docking controller shall publish `/dock_done = False` and transition to `ABORT` if the marker is continuously invisible for 30 seconds during any active docking state, or if any single docking state remains active for more than 45 seconds.

**FR-23** — The docking controller shall transition to `OBSTACLE_AVOIDANCE` when a proximate obstacle is detected during any docking state (except `FINAL_APPROACH`, `SPECIAL_SEARCH`, `DONE`, `ABORT`, and `IDLE`), and subsequently perform a 360° rotation scan (`SPECIAL_SEARCH`) to re-acquire the marker.

### Payload Delivery

**FR-24** — The shooter controller shall deliver exactly three ping-pong balls per docking event, using a rack-and-pinion servo mechanism actuated via GPIO through `pigpio`.

**FR-25** — For the static receptacle (`shoot_type = static`), the shooter shall fire three shots with the following inter-shot delays: ~0.1 s between shots 1 and 2, and ~7.1 s between shots 2 and 3.

**FR-26** — For the dynamic receptacle (`shoot_type = dynamic`), the shooter shall poll an ultrasonic sensor (HC-SR04 or equivalent) at regular intervals and only trigger each shot when the measured distance to the moving receptacle is ≤ 0.70 m, using a two-pass load-then-launch sequence.

**FR-27** — The shooter shall use a median of multiple ultrasonic samples per measurement to reduce noise, filtering out readings outside the valid range of `0.02 m` to `4.0 m`.

**FR-28** — The shooter controller shall publish `/shoot_done = True` upon successful completion of the full delivery sequence and `/shoot_done = False` on any exception during hardware actuation.

**FR-29** — The shooter controller shall support an `enable_hardware = False` simulation mode that completes the delivery sequence after a configurable delay without actuating any GPIO pins.

---

## Non-Functional Requirements

**NFR-01** — The entire mission stack shall be launchable with a single top-level `ros2 launch` command for both the simulation and real-hardware configurations.

**NFR-02** — The system shall expose stable, documented ROS 2 topic contracts (topic names, message types, QoS profiles) so that each subsystem can be developed, tested, and replaced independently.

**NFR-03** — All tunable parameters (speeds, thresholds, timeouts, pin assignments, servo pulse widths) shall be exposed as ROS 2 parameters configurable at launch time via a `params.yaml` file, with no hardcoded values in business logic.

**NFR-04** — The documentation shall be written in Markdown and remain compatible with GitHub Pages rendering.

**NFR-05** — The system shall log all state transitions and key sensor readings to `/rosout` at the `INFO` level to support post-run debugging.

---

## Constraints

**CON-01** — The robot platform is a TurtleBot3 Burger. No modifications to the core drive train or LiDAR mounting are permitted.

**CON-02** — The software stack shall target ROS 2 Humble on Ubuntu 22.04.

**CON-03** — Line-following techniques are prohibited. Navigation must be SLAM and sensor-based.

**CON-04** — The robot shall operate fully autonomously from the moment the mission clock starts. No teleoperation is permitted during the mission.

**CON-05** — The mission must be completed within 25 minutes.

**CON-06** — No more than six ArUco landmark markers may be used across the entire arena.

**CON-07** — The LiDAR's 360° field of view must not be obstructed by any mechanical or storage component mounted on the robot.

**CON-08** — The compute responsibilities are split: the Raspberry Pi 4 (on-board) handles camera processing, docking, and hardware actuation; the remote laptop handles SLAM, navigation, and the FSM.

---

## Performance Requirements

**PR-01** — The robot shall align with delivery receptacles with a lateral positional error of no more than ±10 cm at the point of delivery.

**PR-02** — The ball dispensing success rate (ball lands and remains inside the receptacle) shall be at least 70% per shot under normal operating conditions.

**PR-03** — The exploration algorithm shall cover at least 80% of the accessible arena area before declaring the map fully explored.

**PR-04** — The ArUco marker detection pipeline shall process camera frames in real time (≥10 Hz) and publish pose data with a latency of no more than 200 ms from frame capture.

**PR-05** — The docking controller shall complete a full docking sequence (from `SEARCH` to `DONE`) within 45 seconds per docking attempt under normal visibility conditions.

---

## Interface Requirements

**IR-01** — The operator shall be able to start the full mission stack by typing a single `ros2 launch` command on the remote laptop and a single bringup command on the Raspberry Pi.

**IR-02** — An RViz instance shall be available on the remote laptop during the mission, displaying the live occupancy grid, robot pose, and planned path.

**IR-03** — All inter-subsystem communication shall use standard ROS 2 message types (`Twist`, `Bool`, `String`, `LaserScan`, `OccupancyGrid`, `Odometry`, `TFMessage`, `Image`, `CameraInfo`). No custom message types are used.

---

## Operating Environment

**OE-01** — The arena is an indoor, flat-floored warehouse-style maze with walls tall enough to be detected by the TurtleBot3's LiDAR (minimum wall height: 20 cm).

**OE-02** — ArUco markers are placed in well-lit positions. The camera must be able to detect markers from at least 1.5 m distance under ambient indoor lighting.

**OE-03** — The dynamic receptacle moves laterally within a fixed range. The ultrasonic sensor mounted on the robot must have a clear line of sight to the receptacle during the delivery phase.

---

## Safety Requirements

**SR-01** — The system shall stop all motor output (publish zero-velocity `Twist`) whenever transitioning to the `DONE`, `ABORT`, or `END` states.

**SR-02** — The `destroy_node()` method of each controller node shall publish a zero-velocity `Twist` before shutting down, preventing runaway motion on node death.

**SR-03** — The shooter hardware (servos, GPIO) shall be safely de-energised in the `ShooterController.destroy_node()` method, setting all servo pulse widths to 0 and releasing the `pigpio` connection.

**SR-04** — The system may be interrupted at any time with `Ctrl+C`. All nodes shall handle `KeyboardInterrupt` gracefully and execute their shutdown procedures.

**SR-05** — Physical intervention (catching or stopping the robot) by the operator is permitted if the robot is observed to be causing damage to the arena or to itself.

---

## Acceptance Criteria

| ID | Criterion | Pass Condition |
|---|---|---|
| AC-01 | Single-command launch | Full stack starts without errors from one `ros2 launch` command |
| AC-02 | Map construction | A populated occupancy grid is visible in RViz within 30 s of launch |
| AC-03 | Frontier exploration | Robot visits at least 80% of accessible arena area before `/map_explored = True` |
| AC-04 | Marker detection | `/marker_detected = True` published within 3 s of a marker entering the camera frame |
| AC-05 | Zone discrimination | FSM correctly identifies `static` vs `dynamic` zone from marker ID in all test runs |
| AC-06 | Successful docking | Robot stops within ±10 cm laterally of the receptacle centre in ≥ 80% of docking attempts |
| AC-07 | Static delivery | All 3 balls delivered into the static receptacle without the shooter faulting |
| AC-08 | Dynamic delivery | At least 2 of 3 balls delivered into the moving receptacle across a full mission run |
| AC-09 | Fault recovery | FSM returns to `EXPLORE` within 5 s of a docking `ABORT` signal |
| AC-10 | Safe shutdown | Robot stops completely within 1 s of `Ctrl+C`; no GPIO pins remain energised |

---

## Requirement Traceability

| Requirement | Primary Doc | Validation Doc |
|---|---|---|
| FR-01, FR-02, FR-03, FR-04, FR-05 | [Software Subsystem: Navigation and FSM](subsystem-nav-fsm.md) | [Testing Documentation](testing-documentation.md) |
| FR-06, FR-07, FR-08, FR-09, FR-10 | [Software Subsystem: ArUco Marker Detection](subsystem-software-aruco.md) | [Testing Documentation](testing-documentation.md) |
| FR-11 – FR-17 | [Software Subsystem: Navigation and FSM](subsystem-nav-fsm.md) | [Interface Control Document](interface-control-document.md) |
| FR-18 – FR-23 | [High Level Design](high-level-design.md) | [Testing Documentation](testing-documentation.md) |
| FR-24 – FR-29 | [Electrical Subsystem](subsystem-electrical.md) | [Testing Documentation](testing-documentation.md) |
| NFR-01, NFR-02, NFR-03 | [Software and Firmware Development](software-firmware-development.md) | [User Manual](user-manual.md) |
| NFR-04 | [Home](index.md) | — |
| NFR-05 | [Software and Firmware Development](software-firmware-development.md) | [Testing Documentation](testing-documentation.md) |
| CON-01 – CON-08 | [High Level Design](high-level-design.md) | — |
| PR-01 – PR-05 | [High Level Design](high-level-design.md) | [Testing Documentation](testing-documentation.md) |
| IR-01 – IR-03 | [Interface Control Document](interface-control-document.md) | [User Manual](user-manual.md) |
| SR-01 – SR-05 | [Software and Firmware Development](software-firmware-development.md) | [Testing Documentation](testing-documentation.md) |

---

## Open Assumptions

- The operator launches the system from the documented workspace with the correct ROS 2 environment sourced.
- Camera and LiDAR topics are available and publishing at the expected rates in the selected runtime mode before the mission clock starts.
- The arena walls and obstacles are detectable by the TurtleBot3's LiDAR at all points in the maze.
- The dynamic receptacle's period of motion is slow enough for the ultrasonic-gated delivery approach to achieve at least one valid shot window per polling cycle.
