## [2.6.0] - 2026-04-09
Integrated package updates, enhancing the docking controller with timeout and target marker capabilities, improving the mission controller's zone tracking and launch completion handling, and refining ArUco marker detection. Removed the redundant pose subscriber.

### Added / Changed
- feat(auto_explore.docking): Added `dock_cycle_timeout_sec` and `target_marker_id` parameters to `docking_controller.py` for improved control and specific marker targeting.
- feat(auto_explore.mission_control): Enhanced `mission_controller.py` with dynamic zone tracking via TF, robust launch completion handling, and refined state transitions for docking and exploration.
- feat(auto_explore.aruco): Updated `marker_size_m` to `0.053` and adjusted camera subscription QoS to `qos_profile_sensor_data` in `pose_publisher.py`.
- feat(auto_explore.config): Adjusted `speed` parameter in `params.yaml` to `0.09`.

### Fixed
- fix(auto_explore.aruco): Removed the deprecated `pose_subscriber.py` node.
- fix(auto_explore.docking): Improved `dock_done` publishing logic in `docking_controller.py` to prevent duplicates and log success/failure.
- fix(auto_explore.aruco): Optimized `marker_detected` publishing in `pose_publisher.py` to only trigger on visibility state changes.

## [2.5.0] - 2026-04-09
Implemented advanced zone management in the FSM, enabling dynamic identification and tracking of ArUco marker zones using TF, and preventing re-visitation.

### Added / Changed
- feat(fsm): Implemented dynamic zone identification within `fsm_code.py` by subscribing to `/tf` messages, distinguishing between "static" (`aruco_marker_0`) and "dynamic" (`aruco_marker_1`) zones.
- feat(fsm): Introduced a mechanism in `fsm_code.py` to track and prevent re-visiting already processed zones, ensuring unique marker interactions.
- feat(fsm): Updated the `/zone` publisher in `fsm_code.py` to dynamically publish the identified "static" or "dynamic" zone during "DOCK" and "LAUNCH" states, replacing the previous hardcoded "static" value.
- feat(fsm): Modified the FSM's "EXPLORE" state transition in `fsm_code.py` to require an identified `current_zone` before initiating a "DOCK" sequence.
- feat(fsm): Adjusted `self.required_markers` in `fsm_code.py` from 3 to 2.

## [2.4.1] - 2026-04-09
Refined ArUco marker detection status publishing and improved docking state machine logic.

### Fixed
- fix(marker_detection): Implemented a `/marker_detected` boolean publisher in `Pose_publisher_V2_TF2.py` to indicate ArUco marker visibility.
- fix(docking): Updated `MoveOnAruco` node to use `/cmd_vel_docking` and refined state transitions for `IDLE`, `DONE`, and `ABORT` states in `Aruco_Docker_Final.py`.

## [2.4.0](https://github.com/Kmyming/CDE2310_G10_2526/pull/28) - 2026-04-08
Implemented a command velocity multiplexer within the FSM to dynamically switch between navigation and docking commands, and introduced a "static" zone publisher for docking and launch states.

### Added / Changed
- feat(fsm): Added a command velocity multiplexer in `fsm_code.py` to publish `/cmd_vel` based on the current FSM state, switching between `/cmd_vel_nav` and `/cmd_vel_docking` inputs.
- feat(fsm): Introduced a `/zone` publisher in `fsm_code.py` to indicate "static" zones during "DOCK" and "LAUNCH" states, supporting static/dynamic docking state management.

## [2.3.0] - 2026-04-07
Enhanced exploration visualization and control logic with path publishing capabilities in RViz2 and comprehensive exploration package documentation.

### Added / Changed
- feat(exploration): Added path publishing for exploration visualization in RViz2 to display the robot's navigation path during autonomous exploration.
- feat(exploration): Enhanced path publishing with dynamic start index to provide more granular control over visualization of exploration trajectories.
- feat(exploration): Introduced comprehensive README.md with configuration and usage instructions for the autonomous exploration package.
- feat(exploration): Improved local control logic with enhanced obstacle avoidance and navigation capabilities.
- feat(exploration): Added publisher for map exploration status to notify the FSM of exploration completion.
- feat(config): Adjusted speed parameter in `params.yaml` for improved exploration performance.

### Documentation
- docs(exploration): Added example images for physical test maze to guide manual testing procedures.

## [2.2.0] - 2026-04-07
Implemented autonomous docking capabilities using ArUco markers and enhanced payload delivery servo control.

### Added / Changed
- feat(docking): Introduced a new `MoveOnAruco` node for autonomous docking, utilizing ArUco marker pose data, odometry, and LIDAR for alignment and obstacle avoidance.
- feat(shooting): Added a `set_servo_angle` method for precise servo control in the payload delivery system.

### Fixed
- fix(servo): Corrected the gate opening and closing mechanism in the payload delivery system to use PWM for smoother servo operation.
- fix(aruco): Updated the ArUco pose publisher to correctly detect and process 4x4 ArUco markers.

## [2.1.1] - 2026-03-31
Updated CI workflow documentation to reflect automated changelog generation.

### Documentation
- docs(README): Removed manual instructions for triggering the changelog update, reflecting the automated process.

## [2.1.0] - 2026-03-31
Further enhanced the CI/CD pipeline with automated PR description, review, and code improvement capabilities, alongside comprehensive documentation updates.

### Added / Changed
- feat(ci): Integrated automated PR description, review, and code improvement functionalities into the CI pipeline using the native Python PR-Agent CLI.

### Documentation
- docs(README): Expanded the CI/CD documentation in the README, detailing the AI pipeline steps, manual PR-Agent commands, and including a Mermaid architecture diagram.

## [2.0.0] - 2026-03-31
Major redesign of the launcher payload system, alongside significant enhancements to the CI/CD pipeline for automated changelog generation and PR agent functionality.

### Added / Changed
- feat(payload): Redesigned the launcher payload system, marking a major architectural change.
- feat(cad): Introduced an ultimate pipeline test for CAD assets.
- feat(ci): Implemented native Python CLI execution for PR Agent changelog updates within the CI workflow, including explicit model configuration (`gemini/gemini-2.5-flash`) and refined commit fetching logic.
- feat(ci): implemented an automated commit scraper to read local git history (`git log`) and inject commit messages directly into PR descriptions. This successfully bridges the "binary blindspot," allowing the AI to read physical hardware/CAD updates (`.SLDPRT`, `.STL`) even when the `git diff` is empty.
- feat(ci): added a native Python execution step (`pip install pr-agent`) to trigger the `update_changelog` tool automatically on PR creation, completely bypassing hardcoded event-trigger limitations in the official Qodo Docker image.
- feat(ci): configured PR-Agent to utilize Google's `gemini-2.5-flash` model natively.
- feat(ci): implemented a massive 1,000,000 custom token limit override (`--config.custom_model_max_tokens=1000000`) to prevent the agent from panicking when reading massive hardware repository diffs.

### Documentation
- docs(README): Updated CI documentation and PR agent prompt details in the README.

### Changed
- refactor(ci): transitioned from the official `qodo-ai/pr-agent` Action and Docker image wrappers to a raw CLI execution environment. This prevents environment variable corruption and syntax stripping by the Ubuntu bash runner.
- refactor(ci): shifted model configuration definitions from Bash environment variables to direct CLI arguments (`--config.model="..."`) to bypass the buggy Dynaconf settings parser.

### Fixed
- fix(ci): pinned the `httpx` library to `<0.28.0` in the GitHub Actions runner to prevent fatal `AsyncClient.__init__()` proxy crashes inside the LiteLLM router when falling back to default models.
- fix(ci): resolved `400 Invalid API Key` and LiteLLM authentication errors by routing the GitHub secret explicitly to the `GEMINI_API_KEY` variable required by the native Python environment.

## [1.2.0](https://github.com/Kmyming/CDE2310_G10_2526/pull/18) - 2026-03-31

Integrate marker detection into the FSM, adding a new subscriber and refining callback logic for robust state transitions.

### Added
- feat(fsm): Added a new subscriber for the `/marker_detected` topic in `FSM/fsm_code.py`.

### Fixed
- fix(fsm): Refined the `aruco_callback` logic in `FSM/fsm_code.py` to correctly check `msg.data` in addition to the FSM being in the "EXPLORE" state before setting `self.marker_detected`.

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
  
---
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
