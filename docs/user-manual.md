---
title: User Manual
description: Operator setup, run steps, troubleshooting, and BOM.
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

# User Manual

## Intended Audience

Operators running the robot in simulation or on the TurtleBot3 hardware.

## Prerequisites

- ROS2 Humble
- TurtleBot3 workspace built successfully
- Required hardware connected for real-robot runs
- TurtleBot3 model set correctly for simulation (`burger`)

## Installation

```bash
cd ~/turtlebot3_ws/src
git clone https://github.com/Kmyming/CDE2310_G10_2526.git CDE2310_G10_2526
cd ~/turtlebot3_ws
colcon build --packages-select auto_explore
source install/setup.bash
```

## Startup Procedure

### Simulation

Terminal 1:

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

Terminal 2:

```bash
ros2 launch auto_explore global_bringup.py \
	use_sim_time:=true \
	enable_slam:=true \
	enable_rviz:=false \
	enable_fsm:=true \
	enable_navigation:=true \
	enable_markers:=true \
	enable_pose_publisher:=true \
	enable_docking:=false \
	enable_shooter:=false
```

### Real robot

Terminal 1:

```bash
ros2 launch turtlebot3_bringup robot.launch.py
```

Terminal 2:

```bash
ros2 launch auto_explore global_bringup.py \
	use_sim_time:=false \
	enable_slam:=true \
	enable_rviz:=true \
	enable_fsm:=true \
	enable_navigation:=true \
	enable_markers:=true \
	enable_pose_publisher:=true \
	enable_docking:=true \
	enable_shooter:=true \
	shooter_enable_hardware:=true
```

For shooter host and ultrasonic tuning parameters, use `global_controller_bringup.py` directly.

## Shutdown Procedure

- Stop the launch session.
- Kill any stale robot-side processes if needed.

## Operating Modes

- Simulation mode.
- Real-robot mode.

Shooter delivery modes:

- `static`
- `dynamic`
- `bonus`

Publish mode command:

```bash
ros2 topic pub --once /shoot_type std_msgs/String "data: static"
```

## Troubleshooting

- Missing map or scan.
- RViz not visible.
- Marker detection not producing output.

Common checks:

```bash
ros2 node list
ros2 topic list
ros2 topic list | grep -E '^/map$|^/scan$|^/aruco/debug$|^/states$'
```

## Bill of Materials

| Qty | Item | Purpose | Notes |
|---|---|---|---|
| 1 | TurtleBot3 Burger | Mobile robot base | Main platform |
| 1 | Camera sensor | Marker detection input | Required for ArUco pipeline |
| 1 | LiDAR | Mapping and navigation input | Used by SLAM and exploration |
| 1 | Shooter hardware | Payload delivery | Hardware gate controlled at launch |
