## [1.0.0] - 2026-03-25 [*](https://github.com/Kmyming/CDE2310_G10_2526/pull/13)

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
- feat(DevOps): Created automated CI/CD Pipeline for changelog documentation

### Changed
- refactor(architecture): Refactored entire mission control system from nested repository structure to independent package
- refactor(package): Updated package discovery mechanism to use ROS2 standard conventions

### Fixed
- fix(discovery): Fix package discovery issue by removing redundant exec_depend entries and setting packages=[package_name] in setup.py
- fix(discovery): Fixed package discovery type changed from `(python)` to `(ros.ament_python)`
- fix(package): Resolved XML parsing errors by removing mixed depend/exec_depend entries
- fix(launcher): Fixed launch wrapper script dependency by properly registering package with ROS2
- fix(setup): Removed wrapper script dependency - now uses direct `ros2 launch` command
- fix(config): Removed redundant exec_depend entries from package.xml
- fix(rviz): Cleaned up orphaned RViz configuration files

### Documentation
- docs(README): Update README.md with clear Gazebo and physical robot launch sequences
- docs(README): Update installation instructions for `auto_explore` package
- docs(README): Keep legacy instructions for `autonomous_exploration` package for reference
- docs(README): Updated the 'LEGACY: Manual Launch' section header in `README.md` to include 'For Testbedding & Reference'.

### Technical Details
- **Package Name:** `auto_explore`
- **Build System:** ament_python
- **ROS2 Version:** Humble
- **Python Version:** 3.x
- **Key Dependencies:** rclpy, geometry_msgs, sensor_msgs, nav_msgs, std_msgs, cv_bridge, opencv-python, pyyaml, slam_toolbox, rviz2

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

