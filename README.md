# TurtleBot3 Autonomous Exploration & Mission Control System

This repository contains the ROS2-based TurtleBot3 mission stack for autonomous exploration, ArUco marker detection, docking, and payload delivery.

The markdown files under [docs/](docs/) are the primary documentation deliverable. GitHub Pages is only a supplementary rendered view of the same content.

## Quick Start

```bash
cd ~/turtlebot3_ws/src
git clone https://github.com/Kmyming/CDE2310_G10_2526.git CDE2310_G10_2526
cd ~/turtlebot3_ws
colcon build --packages-select auto_explore
source install/setup.bash
```

Verify the package is discoverable:

```bash
ros2 pkg list | grep auto_explore
```

## Launch Entry Points

- [Software and Firmware Development](docs/software-firmware-development.md) for the build and launch workflow.
- `remote_laptop_src/launch/global_bringup.py` is the top-level integrated bringup.
- `remote_laptop_src/launch/global_controller_bringup.py` declares the shooter tuning arguments such as `shooter_pigpiod_host`, `shooter_pigpiod_port`, `shooter_ultrasonic_trigger_pin`, `shooter_ultrasonic_echo_pin`, `shooter_ultrasonic_distance_threshold_m`, `shooter_ultrasonic_simulated_distance_m`, and `shooter_engage_profile`.
- `remote_laptop_src/launch/nav_bringup.py` is the navigation-only bringup.

## Simulation Run

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

In a second terminal:

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

## Real Robot Run

```bash
ros2 launch turtlebot3_bringup robot.launch.py
```

Then launch the mission stack:

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

If you need to pass shooter host or ultrasonic tuning arguments, launch `global_controller_bringup.py` directly because those tuning arguments are declared at the controller layer.

## Documentation Map

- [Requirements Specification](docs/requirements-specification.md)
- [Concept of Operations](docs/con-ops.md)
- [High Level Design](docs/high-level-design.md)
- [Software Subsystem: Navigation and FSM](docs/subsystem-nav-fsm.md)
- [Software Subsystem: ArUco Marker Detection](docs/subsystem-software-aruco.md)
- [Mechanical Subsystem](docs/subsystem-mechanical.md)
- [Electrical Subsystem](docs/subsystem-electrical.md)
- [Interface Control Document](docs/interface-control-document.md)
- [Software and Firmware Development](docs/software-firmware-development.md)
- [Testing Documentation](docs/testing-documentation.md)
- [User Manual](docs/user-manual.md)
- [Areas for Improvement](docs/improvements.md)
- [Appendix](docs/appendix.md)

## Notes

- `CHANGELOG.md` is the repository release-history reference.
- The user-facing docs should stay markdown-first.
- GitHub Pages is optional presentation, not the primary submission artifact.
