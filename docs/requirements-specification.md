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

The system must autonomously explore an unknown environment, detect ArUco markers, transition through mission states, and complete docking and payload-delivery behaviors without manual teleoperation.

## Stakeholder Needs

- Autonomous exploration of unknown space.
- Reliable detection and logging of markers.
- Deterministic mission transitions.
- Clear operator setup and shutdown procedures.

## Functional Requirements

- FR-01: Build a map and explore frontiers using ROS2 navigation inputs.
- FR-02: Detect ArUco markers from camera input and publish pose data.
- FR-03: Transition between explore, dock, launch, and end states using mission logic.
- FR-04: Allow simulation and real-robot operation through launch arguments.
- FR-05: Support shooter hardware gating through launch-time parameters.

## Non-Functional Requirements

- NFR-01: The system shall be launchable with a single top-level bringup.
- NFR-02: The system shall expose stable topic contracts for integration.
- NFR-03: The documentation shall remain markdown-first and Pages-compatible.

## Constraints

- ROS2 Humble environment.
- TurtleBot3 Burger hardware and camera availability.
- Separate laptop and robot runtime responsibilities.

## Acceptance Criteria

- The robot can start from the documented launch sequence.
- Navigation, markers, and mission control can be launched independently.
- The full mission stack exposes the expected topics and launch arguments.

## Requirement Traceability

| Requirement | Primary doc | Validation doc |
|---|---|---|
| FR-01 | [High Level Design](high-level-design.md) | [Testing Documentation](testing-documentation.md) |
| FR-02 | [Software Subsystem: ArUco Marker Detection](subsystem-software-aruco.md) | [Testing Documentation](testing-documentation.md) |
| FR-03 | [High Level Design](high-level-design.md) | [Interface Control Document](interface-control-document.md) |
| FR-04 | [Software and Firmware Development](software-firmware-development.md) | [User Manual](user-manual.md) |
| FR-05 | [Interface Control Document](interface-control-document.md) | [Testing Documentation](testing-documentation.md) |

## Open Assumptions

- The operator will launch the system from the documented workspace.
- The camera and LiDAR topics are available in the selected runtime mode.
