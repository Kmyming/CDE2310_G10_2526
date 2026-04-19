---
title: High Level Design
description: System architecture and mission data flow.
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

# High Level Design

## System Overview

The system is split between a laptop-side orchestration layer and robot-side hardware bringup. The laptop runs the mission controller, navigation stack, and visualization; the robot provides motion, sensing, and actuation support.

## Deployment Architecture

- Laptop: `global_bringup.py`, SLAM, RViz, FSM, navigation orchestration.
- Robot: bringup processes, camera feed, and hardware-facing control.

## Runtime Components

- Mission controller
- Exploration controller
- Marker detection node
- Docking controller
- Shooter controller
- SLAM Toolbox
- RViz

## Data Flow

- Sensor data enters through LiDAR and camera topics.
- SLAM builds and updates the map.
- Navigation consumes map, odometry, and scan data.
- Marker detection publishes pose output for mission logic.
- Mission control decides when to transition states.

## ROS Graph Summary

The ROS graph centers on `/map`, `/odom`, `/scan`, `/aruco/debug`, `/states`, `/cmd_vel`, `/dock_done`, and `/shoot_type`.

## Mission State Flow

EXPLORE -> DOCK -> LAUNCH -> EXPLORE -> END

## Design Rationale

- Separate launch layers reduce coupling.
- Boolean launch arguments allow selective subsystem bringup.
- Markdown-first documentation keeps design, operation, and testing aligned.
