---
title: Software Subsystem: ArUco Marker Detection
description: Camera-based ArUco detection and pose publication.
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

# Software Subsystem: ArUco Marker Detection

## Purpose

Detect ArUco markers from the camera stream and publish marker pose information for the mission controller and logging tools.

## Runtime Entry Point

The node is launched through `remote_laptop_src/launch/global_controller_bringup.py` when marker processing is enabled.

## Launch Interface

- `enable_markers`
- `enable_pose_publisher`

## Detection Pipeline

- Subscribe to image and camera-info topics.
- Detect tags using the configured dictionary and marker size.
- Estimate pose and publish output for downstream consumers.

## Camera and Calibration Inputs

- `/camera/image_raw`
- `/camera/camera_info`

## Output Topics

- `/aruco/debug`
- Marker pose output for mission logic

## Logging Behavior

- Marker observations should be visible in the runtime logs.
- The logger subsystem is responsible for persistent file capture.

## Failure Modes

- Missing camera feed.
- Invalid camera intrinsics.
- No markers in view.
