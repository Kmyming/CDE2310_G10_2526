---
title: User Manual
description: Operator setup, run steps, troubleshooting, and BOM.
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

# User Manual

## End User Documentation
<div style="text-align: center; margin: 2rem 0;">
  <iframe 
    src="assets/END USER DOC.pdf" 
    width="80%" 
    height="600px" 
    style="border: none; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);"
  >
  </iframe>
  <p>
    <a href="assets/END USER DOC.pdf" target="_blank" style="text-decoration: none;">
      📄 View PDF in a new tab
    </a>
  </p>
</div>

## Prerequisites

- ROS2 Humble
- TurtleBot3 workspace built successfully
- Required hardware connected for real-robot runs
- TurtleBot3 model set correctly for simulation (`burger`)
- All setup steps in `software-firmware-development.md` completed (dependencies, aliases, cleanup scripts, and launch helpers)

## Launch Sequences

### Gazebo simulation

Terminal 0 (before launch):

```bash
cleanup
```

Terminal 1:

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

Terminal 2:

```bash
ros2 launch auto_explore global_controller_bringup.py use_sim_time:=true \
	enable_fsm:=true enable_navigation:=true enable_markers:=true \
	enable_pose_publisher:=true enable_docking:=true enable_shooter:=true \
	shooter_enable_hardware:=false shooter_pigpiod_host:=<PI_IP_FROM_BOOT>
```

### Physical TurtleBot3

Terminal 1:

if rosbu & cleanup script is not set up:
```bash
ros2 launch turtlebot3_bringup robot.launch.py
```

else run:
```bash
rosbustop && rosbu
```

Terminal 2:

```bash
ros2 launch auto_explore global_controller_bringup.py use_sim_time:=false \
	enable_fsm:=true enable_navigation:=true enable_markers:=true \
	enable_pose_publisher:=true enable_docking:=true enable_shooter:=true \
	shooter_enable_hardware:=true shooter_pigpiod_host:=<PI_IP_FROM_BOOT>
```
If cleanup & start is set up:
Copy the Pi IP shown at boot and pass it to `shooter_pigpiod_host`.
```bash
cleanup && start <PI_IP_FROM_BOOT>
```
If shooter host or ultrasonic tuning arguments are required, launch `global_controller_bringup.py` directly, because those arguments are declared at the controller launch layer.

## Shutdown Procedure

- On the Raspberry Pi terminal running `rosbu`, press `Ctrl+C` to stop all bringup processes.
- On the laptop terminal running `start`, press `Ctrl+C` to stop all mission stack processes.
- Verify both terminals have returned to the shell prompt before the next run.

## Troubleshooting

Use the following live checks during runtime.

### 1) States

Command:

```bash
ros2 topic echo /states std_msgs/msg/String
```

Positive:
- State messages are publishing continuously and state transitions are sensible for mission phase.

Restart required:
- No `/states` output for more than 10 seconds.
- State machine is stuck indefinitely with no expected transition.

### 2) Map (frequency and echo)

Commands:

```bash
ros2 topic hz /map
ros2 topic echo /map --once
```

Positive:
- `/map` exists and publishes steadily.
- `echo --once` returns a valid OccupancyGrid message.

Restart required:
- `/map` topic missing.
- `/map` frequency remains zero for more than 10 seconds after startup delay.
- `echo --once` times out or returns no map data.

### 3) Scan

Commands:

```bash
ros2 topic hz /scan
ros2 topic echo /scan --once
```

Positive:
- `/scan` exists and updates continuously.

Restart required:
- `/scan` missing or no updates for more than 5 seconds.

### 4) TF

Commands:

```bash
ros2 topic hz /tf
ros2 topic echo /tf --once
```

Positive:
- `/tf` is active and broadcasting transforms.

Restart required:
- `/tf` is missing or not publishing.
- Navigation components report persistent transform/timeouts.

### 5) Topics Sanity

Command:

```bash
ros2 topic list | grep -E '^/states$|^/map$|^/scan$|^/tf$'
```

Positive:
- All required topics are present.

Restart required:
- One or more required topics are missing after startup completes.

### 6) RViz Not Pulling Up After Delay

Checks:

```bash
ros2 node list | grep rviz
```

Positive:
- RViz window appears after the configured startup delay.
- `rviz` node is visible in node list.

Restart required:
- RViz does not appear after delay and no `rviz` node is running.
- RViz repeatedly crashes on launch.

### Restart Decision Rule

Do a full system restart (stop `rosbu` and `start` with Ctrl+C, then relaunch) if any critical stream (`/states`, `/map`, `/scan`, `/tf`) fails the checks above and does not recover within 10 seconds.
