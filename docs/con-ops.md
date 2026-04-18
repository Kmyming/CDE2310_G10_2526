---
title: Concept of Operations
description: Operator workflow and mission behavior.
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

# Concept of Operations

## Mission Context

The robot starts in a prepared workspace, explores the environment autonomously, detects markers, and transitions into docking and delivery states as mission conditions are met.

## Normal Operating Scenario

1. Operator sets up the workspace and sources the ROS environment.
2. The top-level bringup launches navigation, mission control, and marker processing.
3. The robot explores and publishes mission-state updates.
4. Marker detections trigger downstream mission behavior.
5. The mission ends after the configured completion conditions are satisfied.

## Startup Sequence

- Build the package.
- Source the workspace.
- Launch the correct bringup for simulation or real hardware.
- Confirm the expected topics and nodes are active.

## Exploration Phase

- Navigation controller follows frontier-based exploration.
- SLAM and map updates are used for global context.
- Exploration continues until the mission controller decides to transition.

## Marker Detection Phase

- Camera frames are processed for ArUco tags.
- Pose outputs are logged and published for mission consumption.

## Docking and Shooter Phase

- Mission control enables docking or shooter behavior only when the corresponding state and launch flags are active.
- Hardware actuation remains gated by launch-time configuration.

## Shutdown Sequence

- Stop robot motion.
- End the active launch session.
- Kill any stale robot-side processes before the next run.

## Fault / Recovery Scenarios

- Missing map data: wait for SLAM startup or confirm publishers.
- Missing camera data: check camera topics and calibration.
- Launcher mismatch: verify launch arguments for the selected entrypoint.

## Operator Responsibilities

- Choose sim or real-robot mode.
- Supply the correct launch arguments.
- Monitor topic health and node logs.
