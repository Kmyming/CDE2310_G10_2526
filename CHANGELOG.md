## [2.16.2] - 2026-04-18

### Fixed
- fix(payload): CAD files restructuring

# Changelog
## [2.16.1] - 2026-04-18
### Documentation
- docs(con-ops): Expanded the Concept of Operations document with detailed mission phases, system overview, operational sequences, and fault recovery scenarios.

## [2.16.0] - 2026-04-18
Iterative redesign of the payload launcher for improved feeding, increased launch force, and reduced gear slipping, based on testing results.
### Added / Changed
- feat(payload): Added servo gate mount
- feat (payload): launcher design iteration to prevent gear slipping (add servo cover, reduce servo screw hole diameter, reduce gear distance, increase wall thickness to reduce launcher flex)
- feat (payload): moved ball stop further up to reduce feeding jam and increase launch distance
- feat (payload): side wall addition to prevent ball rolling out during feeding
- feat (payload): increased launcher tilt to reduce ball falling out of launcher

## [2.15.1] - 2026-04-18
### Documentation
- docs(interface): Documented ROS topic specifications, launch arguments, timing, and error handling.
- docs(subsystem): Completed navigation and FSM subsystem design, state flow, and parameter tuning.
- docs(development): Added configuration management guide and comprehensive troubleshooting procedures.

## [2.15.0] - 2026-04-17
### Added / Changed
- feat(navigation): Enhanced frontier group selection and local obstacle avoidance in exploration.
- feat(marker): Implemented a `/marker_detected` publisher in `Pose_publisher_V2_TF2.py` to indicate Aruco marker visibility.

### Fixed
- fix(shooter): Reverted and reorganized shooter delivery logic, including dynamic shot counting, and fine-tuned pinion engagement trim parameters for consistency.
- fix(fsm): Improved FSM handling of docking failures and marker loss during docking.

### Testing
- test(shooter): Added a standalone servo isolation test script (`servo_isolation_test.py`).

## [2.14.0] - 2026-04-15
Introduced a two-pass dynamic delivery sequence for the shooter and improved RViz launch robustness.

### Added / Changed
- feat(shooter): Implemented a two-pass dynamic delivery sequence in `shooter_controller.py`, separating loading and launching phases for dynamic shots.
- feat(launch): Added environment variable prefix to the RViz node in `nav_bringup.py` for cleaner launch and debugging.

### Fixed
- fix(auto_explore): Corrected a typo in the parameter retrieval method for 'marker_size_m' in `pose_publisher.py`.

## [2.13.2] - 2026-04-15
Finalized fine-tuned shooting parameters for improved performance and updated Aruco marker detection.

### Fixed
- fix(shooter): Fine-tuned multiple shooting parameters in `shooter_controller.py`, including `gate_settle_s` to `0.225`, `ball_drop_s` to `0.225`, `disengage_trim_per_extra_cycle_s` to `0.015`, `disengage_trim_per_extra_cycle_high_s` to `0.015`, `rack_hold_duration_s` to `0.2`, `rack_cycle_pause_s` to `0.3`, `delivery2_delay` to `0.1`, `delivery3_delay` to `7.1`, and adjusted `engage_profiles` values. The default `engage_profile` in `_get_engage_time_for_cycle` was also changed to `mild`.
- fix(auto_explore): Adjusted the `marker_size_m` parameter in `pose_publisher.py` from `0.053` to `0.049` for improved Aruco marker detection accuracy.

### Documentation
- docs(shooter): Added instructions to `README.md` for activating the shooter node using `ros2 topic pub` commands for static and dynamic shooting.

## [2.13.1] - 2026-04-15
### Fixed
- fix(docking): Implemented new watchdog timers (30s marker invisibility, 45s state timeout) in `docking_controller.py` to prevent the robot from getting stuck during docking.
- fix(docking): Refactored state transitions in `docking_controller.py` to use a dedicated `set_state` method, ensuring consistent state management and watchdog resets.
- fix(docking): Renamed the `MoveOnAruco` node to `DockingController` and adjusted `mid_tz_threshold` to 0.50 in `docking_controller.py`.

## [2.13.0] - 2026-04-15
Streamlined exploration by removing the yaw rotation sweep at waypoints and introduced a new tight maze simulation environment.

### Added / Changed
- feat(exploration): Eliminated the yaw rotation sweep at waypoints in `exploration_controller.py`, allowing the robot to transition immediately to the next waypoint for improved navigation efficiency.
- feat(simulation): Added a new `tight_maze.world` Gazebo environment for testing navigation in constrained spaces.

## [2.12.0] - 2026-04-15
Major refactor of the docking controller, introduction of delayed startup for SLAM and RViz, and various parameter tunings for SLAM and shooter.

### Added / Changed
- feat(docking): Reworked the `docking_controller.py` FSM to a simpler align-and-approach logic, introducing new configurable parameters for approach speed, angular speed, alignment gain, tolerances, and docking distance.
- feat(launch): Added `slam_start_delay_sec` and `rviz_start_delay_sec` launch arguments to `nav_bringup.py` to delay SLAM Toolbox and RViz startup using `TimerAction`.
- feat(launch): Introduced `enable_pose_publisher` launch argument in `global_bringup.py` and `global_controller_bringup.py` to conditionally enable the `pose_publisher` node.

### Fixed
- fix(slam): Adjusted `throttle_scans`, `minimum_time_interval`, `transform_timeout`, `tf_buffer_duration`, and `scan_buffer_size` in `mapper_params_online_async.yaml` to improve SLAM stability and TF message handling.
- fix(shooter): Tuned `gate_settle_s` and `ball_drop_s` parameters in `shooter_controller.py` for improved timing.

### Documentation
- docs(setup): Updated `README.md` with `shooter_pigpiod_host` in launch commands and added a reusable `start` shell function for simplified deployment.

## [2.11.2] - 2026-04-14
Refined the initial approach distance for the docking maneuver.

### Fixed
- fix(Docking): Adjusted the `mid_tz_threshold` parameter in `docking_controller.py` from 0.50 to 0.30 to refine the initial straight approach limit during docking.

## [2.11.1] - 2026-04-14
Ensured the shooter node has sufficient time to complete its operation during the launch sequence.

### Fixed
- fix(FSM): Implemented a minimum duration for the 'LAUNCH' state in `mission_controller.py` using `launch_min_duration_sec` to ensure the shooter node completes its cycle.
- fix(FSM): Refined 'LAUNCH' state management in `mission_controller.py` to correctly handle `launch_completion_pending` and `launch_start_time` for robust shooter operation.

## [2.11.0] - 2026-04-14
Implemented a new post-launch backup maneuver to prevent collisions and adjusted the robot's yaw sweep rotation speed.

### Added / Changed
- feat(state): Implemented a new "BACKUP" state in `mission_controller.py` that triggers after a launch sequence, causing the robot to move backward at -0.1 m/s for 2 seconds before returning to exploration.
- feat(auto_explore): Reduced the yaw sweep angular velocity in `exploration_controller.py` from `math.pi / 2` (90 deg/s) to `math.pi / 6` (30 deg/s).

## [2.10.1] - 2026-04-14
### Fixed
- fix(FSM): Removed the `/zone` topic publisher and its associated logic from `mission_controller.py`.

## [2.10.0] - 2026-04-14
Implemented a new post-waypoint behavior for the robot to perform a yaw sweep, enhancing its ability to locate objects after reaching a destination.

### Added / Changed
- feat(auto_explore): Added yaw sweep functionality to `exploration_controller.py`, enabling the robot to perform a 360-degree rotation after reaching a waypoint to search for Aruco codes.

## [2.9.6] - 2026-04-14
Integrated a robust, filtered ultrasonic sensing system for improved dynamic payload delivery.

### Fixed
- fix(shooter): Implemented a new callback-based ultrasonic measurement system in `shooter_controller.py` using `pigpio.EITHER_EDGE` callbacks for improved accuracy.
- fix(shooter): Added new parameters for ultrasonic filtering and calibration: `ultrasonic_sample_count`, `ultrasonic_sample_gap_s`, `ultrasonic_min_distance_m`, `ultrasonic_max_distance_m`, and `ultrasonic_temperature_c`.
- fix(shooter): Implemented median filtering for ultrasonic distance readings and a temperature-compensated `_speed_of_sound_m_s` calculation.
- fix(shooter): Ensured proper cleanup of the ultrasonic callback and `ultrasonic_trigger_pin` in `destroy_node`.

## [2.9.5] - 2026-04-13
Tuned various shooter parameters and refined timing logic for improved static payload delivery.

### Fixed
- fix(shooter): Adjusted `gate_close_us`, `gate_settle_s`, `engage_to_gate_open_offset_s`, `ball_drop_s`, `close_to_release_s`, `rack_hold_duration_s`, and `rack_cycle_pause_s` in `shooter_controller.py`.
- fix(shooter): Renamed `engage_trim_per_extra_cycle_s` and `engage_trim_per_extra_cycle_high_s` to `disengage_trim_per_extra_cycle_s` and `disengage_trim_per_extra_cycle_high_s` respectively, updating their values.
- fix(shooter): Updated `engage_us` and `engage_time_s` for the 'medium' engage profile, and refined the `_get_disengage_pause_for_cycle` logic for cycle-dependent disengage pauses.
- fix(shooter): Modified the `_shoot_once_hardware` function to ensure `engage_thread.join()` timing is independent of gate timing.

## [2.9.4] - 2026-04-13
Integrated shooter testbed into auto_explore package. Updated the auto_explore shooter subsystem to support real-hardware operation via pigpio (remote pigpiod) and adds launch/documentation wiring for the new shooter configuration options.

### Fixed
- fix(shooter): Added shooter launch arguments for pigpiod connection details and ultrasonic/delivery tuning, and forwarded them into shooter_controller.
- fix(shooter): Refactored shooter_controller to use pigpio, add delivery modes (static/dynamic/bonus), and run delivery asynchronously with a busy lock.

### Documentation
- docs(README): Updated README/changelog documentation for the new shooter setup and arguments.

## [2.9.3] - 2026-04-12
Refactored the shooter node's architecture to use `pigpio` for gate control, improved the shooting sequence, and ensured proper GPIO cleanup.

### Fixed
- fix(shooter): Architecturally refactored the shooter node (`Payload_Delivery.py`) to use `pigpio` for SG90 gate servo control, enabling parallel rack engagement and gate operation via threading, and corrected the shooting sequence logic. This included proper resource cleanup in `destroy_node()` and refined pinion timing parameters in `Pinion_Rotation.py`. Added offset tuning parameters for control over servo gate & pinion gear activation timing sequence for real world finetuning.

## [2.9.2] - 2026-04-12
Refactored parameter loading for navigation and SLAM to use ROS 2 parameter server mechanisms, and removed the redundant marker logger.

### Fixed
- fix(navigation): Migrated `exploration_controller` to retrieve navigation tuning parameters from the ROS 2 parameter server, deprecating the previous direct YAML file access.
- fix(slam): Implemented dynamic loading of SLAM Toolbox parameters through a new `slam_params_file` launch argument, referencing `mapper_params_online_async.yaml`.
- fix(logging): Discontinued the `pose_subscriber` node, along with its launch arguments and console entry points, due to its redundant marker logging functionality.

### Documentation
- docs(README): Revised `README.md` to document the removal of the marker logger and include a new section for troubleshooting launch file updates.

## [2.9.2] - 2026-04-12
Refined docking activation logic so the docking controller only engages when the FSM is in the docking state, preventing unintended docking behaviour during other mission phases.

### Fixed
- fix(docking): Updated `docking_controller.py` to subscribe to the `/states` topic and track the robot's overall FSM state before initiating docking.
- fix(docking): Modified the docking controller to remain in `IDLE` by default and only transition to `SEARCH` when the FSM publishes `"DOCK"` on `/states`, ensuring docking logic is gated by the main robot state machine.
- fix(docking): Prevented the docking state machine from starting automatically whenever marker data is available, reducing unintended activation outside the intended docking phase.

## [2.9.1] - 2026-04-12
Refactored parameter loading for navigation and SLAM to use ROS 2 parameter server mechanisms, and removed the redundant marker logger.

### Fixed
- fix(navigation): Updated `exploration_controller` to load navigation tuning parameters directly from the ROS 2 parameter server, replacing direct YAML file parsing.
- fix(slam): Integrated SLAM Toolbox parameters via a new dedicated configuration file (`mapper_params_online_async.yaml`) and exposed it as a launch argument (`slam_params_file`).
- fix(logging): Removed the `pose_subscriber` node, its associated launch arguments, and entry points, as it provided redundant marker logging functionality.

### Documentation
- docs(README): Updated `README.md` to reflect the removal of the marker logger, its launch argument, and added a new troubleshooting section for launch file changes.

## [2.9.0] - 2026-04-12
Integrated servo-driven pinion for payload delivery, enhanced FSM communication with launch completion signals, and refined shooting timings.

### Added / Changed
- feat(shooter): Integrated `Pinion_Rotation` module for servo-controlled rack and pinion payload delivery, replacing direct GPIO rack control in `Shooter/Payload_Delivery.py`.
- feat(fsm): Implemented publishing to `/launch_done` topic from `Shooter/Payload_Delivery.py` after static, dynamic, or bonus deliveries.
- feat(shooter): Adjusted `PHASE1_DEGREES` to `180` in `Shooter/Pinion_Rotation.py` for improved rack engagement.

### Fixed
- fix(shooter): Updated GPIO pin for gate control from `17` to `12` in `Shooter/Payload_Delivery.py`.
- fix(shooter): Tuned shooting timings, including `delivery2_delay` and servo angle hold duration in `Shooter/Payload_Delivery.py`.
- fix(shooter): Ensured proper motor stop and cleanup after `run_cycle` in `Shooter/Pinion_Rotation.py`.

## [2.8.0] - 2026-04-11
Refined shooter mechanism parameters for enhanced performance and updated documentation for new launch configurations.

### Added / Changed
- feat(shooter): Tuned shooter parameters in `Shooter/Pinion_Rotation.py` for drift calibration and continuous shooting, introducing configurable engagement profiles (mild, medium, strong), per-cycle engagement time trimming, and updated timing parameters (`HOLD_DURATION`, `CYCLE_PAUSE`, `ENGAGE_US`, `DISENGAGE_US`, `ENGAGE_TIME_S`, `DISENGAGE_TIME_S`, `ENGAGE_TRIM_PER_EXTRA_CYCLE_S`, `ENGAGE_TRIM_PER_EXTRA_CYCLE_S_2`, `ENGAGE_MIN_TIME_S`).

### Documentation
- docs(README): Updated `README.md` to include the `shooter_enable_hardware` launch argument and clarified launch command usage.

## [2.7.0] - 2026-04-11

Introduced a new hardware control script for the shooter's rack and pinion mechanism, enabling precise servo-driven engagement and disengagement.

### Added / Changed
- feat(shooter): Implemented `Shooter/Pinion_Rotation.py` to control an MG90S continuous rotation servo for a rack and pinion system using `pigpio` on Raspberry Pi. This includes functions for forward rotation, stopping, timed degree rotation, and a full cycle of engaging, holding, and disengaging the rack.

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
