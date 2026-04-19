---
title: Interface Control Document
description: ROS topic, launch argument, and integration contracts.
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

# Interface Control Document

## Interface Scope

This document defines the launch arguments, ROS topics, and ownership boundaries used by the integrated `auto_explore` package.

## ROS Topics


| Topic | Type | Primary Owner | Purpose |
|---|---|---|---|
| `/map` | `nav_msgs/msg/OccupancyGrid` | SLAM Toolbox | Global map updates |
| `/odom` | `nav_msgs/msg/Odometry` | Robot base | Robot pose and velocity |
| `/scan` | `sensor_msgs/msg/LaserScan` | LiDAR | Obstacle and frontier sensing |
| `/states` | `std_msgs/msg/String` | Mission controller | FSM state publication |
| `/aruco/debug` | `std_msgs/msg/String` | Pose publisher | Marker debug and pose payload |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Navigation controller | Base velocity command |
| `/dock_done` | `std_msgs/msg/Bool` | Docking controller | Dock completion signal |
| `/shoot_type` | `std_msgs/msg/String` | Mission controller | Shooter mode trigger |

## Message Types

Topic type contracts above are the runtime reference and should be revalidated after interface changes.

## Publish / Subscribe Ownership

- Navigation consumes map, odometry, and scan data.
- Mission control publishes state transitions.
- Marker detection publishes marker pose information.

## Launch Arguments

### Top-level integrated launcher (`global_bringup.py`)

- `use_sim_time`
- `enable_slam`
- `enable_rviz`
- `slam_params_file`
- `enable_fsm`
- `enable_navigation`
- `enable_markers`
- `enable_pose_publisher`
- `enable_docking`
- `enable_shooter`
- `shooter_enable_hardware`

### Controller launcher (`global_controller_bringup.py`)

- `use_sim_time`
- `nav_params_file`
- `enable_fsm`
- `enable_navigation`
- `enable_markers`
- `enable_pose_publisher`
- `enable_docking`
- `enable_shooter`
- `shooter_enable_hardware`
- `shooter_pigpiod_host`
- `shooter_pigpiod_port`
- `shooter_ultrasonic_trigger_pin`
- `shooter_ultrasonic_echo_pin`
- `shooter_ultrasonic_distance_threshold_m`
- `shooter_ultrasonic_simulated_distance_m`
- `shooter_engage_profile`

### Navigation launcher (`nav_bringup.py`)

- `use_sim_time`
- `enable_slam`
- `enable_rviz`
- `slam_params_file`
- `slam_start_delay_sec`
- `rviz_start_delay_sec`

### Important propagation note

`global_bringup.py` is the integrated entrypoint, but shooter tuning arguments are declared in `global_controller_bringup.py`. If host/ultrasonic tuning is required, launch the controller bringup directly or update argument forwarding.

## Timing and Rates

- Record launch-delay expectations here.
- Document any loop rates used by controllers.

## Error and Fallback Behavior

- Define how each subsystem behaves when inputs are missing.

## Interface Change Rules

- Update this document whenever a topic, message, or launch argument changes.
