# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0](https://github.com/Kmyming/CDE2310_G10_2526/pull/17) - 2026-03-26

Refactored the FSM state machine logic, removing obsolete components, improving state transition reliability, and enhancing overall mission control clarity.

### Added / Changed
- feat(fsm): Increased the `required_markers` count from 2 to 3 in `FSM/fsm_code.py`.
- feat(fsm): Improved logging messages for state transitions and added type hints for callback functions in `FSM/fsm_code.py`.

### Fixed
- fix(fsm): Removed unused `PoseStamped` import, `current_marker_pub` publisher, and `aruco_pose` subscriber from `FSM/fsm_code.py`.
- fix(fsm): Refined the `EXPLORE` state logic in `FSM/fsm_code.py` to correctly transition to `DOCK` or `END`, removing a redundant `self.change_state("EXPLORE")` call.
- fix(fsm): Added `self.timer.cancel()` in the `END` state of `FSM/fsm_code.py` to stop the state machine loop and prevent continuous logging after mission completion.

## [1.0.0] - 2026-03-20

Complete architectural refactor: Independent `auto_explore` mission control system with modular ROS2 launch architecture, proper package discovery, and updated documentation.

### Added
- feat(architecture): Create independent `auto_explore` mission control system with zero external imports
- feat(launch): Implement modular launch architecture with 3 components (nav_bringup, global_controller_bringup, global_bringup)
- feat(fsm): Port FSM state machine from legacy implementation to `mission_controller.py`
- feat(navigation): Port frontier-based exploration algorithm from legacy to `exploration_controller.py`
- feat(markers): Port ArUco marker detection from legacy to `pose_publisher.py`
- feat(markers): Port marker logging system from legacy to `pose_subscriber.py`
- feat(config): Create local `config/params.yaml` for exploration parameter tuning (lookahead_distance, speed, expansion_size, target_error, robot_r)
- feat(package): Implement proper ROS2 ament_python package structure with correct buildtool_depend and export section
- fix(discovery): Fix package discovery issue by removing redundant exec_depend entries and setting packages=[package_name] in setup.py
- docs(README): Update README.md with clear Gazebo and physical robot launch sequences
- docs(README): Update installation instructions for `auto_explore` package
- docs(README): Keep legacy instructions for `autonomous_exploration` package for reference

### Changed
- refactor(architecture): Refactored entire mission control system from nested repository structure to independent package
- refactor(package): Updated package discovery mechanism to use ROS2 standard conventions

### Fixed
- fix(discovery): Fixed package discovery type changed from `(python)` to `(ros.ament_python)`
- fix(package): Resolved XML parsing errors by removing mixed depend/exec_depend entries
- fix(launcher): Fixed launch wrapper script dependency by properly registering package with ROS2
- fix(setup): Removed wrapper script dependency - now uses direct `ros2 launch` command
- fix(config): Removed redundant exec_depend entries from package.xml
- fix(rviz): Cleaned up orphaned RViz configuration files

### Technical Details
- **Package Name:** `auto_explore`
- **Build System:** ament_python
- **ROS2 Version:** Humble
- **Python Version:** 3.x
- **Key Dependencies:** rclpy, geometry_msgs, sensor_msgs, nav_msgs, std_msgs, cv_bridge, opencv-python, pyyaml, slam_toolbox, rviz2

