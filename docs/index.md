---
title: TurtleBot3 Autonomous Exploration & Mission Control System
description: Entry point for the project documentation set.
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

# TurtleBot3 Autonomous Exploration & Mission Control System

## Overview

This project implements a ROS2-based TurtleBot3 mission stack for autonomous exploration, ArUco marker detection, docking, and payload delivery. The repository is documented in markdown first; GitHub Pages is a supplementary rendered view of the same content.

## Project Snapshot

| Item | Value |
|---|---|
| Platform | TurtleBot3 Burger |
| ROS2 | Humble |
| Primary package | `auto_explore` |
| Runtime split | Laptop for mission control and SLAM, robot for bringup and hardware |
| Main launch entrypoint | `remote_laptop_src/launch/global_bringup.py` |

## Documentation Map

- Requirements and scope: [Requirements Specification](requirements-specification.md)
- Operating concept: [Concept of Operations](con-ops.md)
- Architecture: [High Level Design](high-level-design.md)
- Software navigation: [Software Subsystem: Navigation and FSM](subsystem-nav-fsm.md)
- Marker detection: [Software Subsystem: ArUco Marker Detection](subsystem-software-aruco.md)
- Physical build: [Mechanical Subsystem](subsystem-mechanical.md)
- Wiring and power: [Electrical Subsystem](subsystem-electrical.md)
- ROS interfaces: [Interface Control Document](interface-control-document.md)
- Build and deployment: [Software and Firmware Development](software-firmware-development.md)
- Validation: [Testing Documentation](testing-documentation.md)
- Operator guide: [User Manual](user-manual.md)
- Future work: [Areas for Improvement](improvements.md)
- [Appendix](appendix.md)

## GitHub Pages

The Pages site should mirror these markdown files using a simple Jekyll theme. It is a presentation layer only; the md files are the canonical submission artifacts.

