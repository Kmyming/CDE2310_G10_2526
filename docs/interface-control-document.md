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

## Document Purpose

This is the **authoritative reference for system contracts**: ROS topic definitions, launch arguments, message types, timing specifications, and error handling. This document defines WHAT interfaces exist and HOW they behave.

**Other documentation references this document for specifications:**
- [software-firmware-development.md](software-firmware-development.md) - HOW to build, deploy, and troubleshoot
- [subsystem-nav-fsm.md](subsystem-nav-fsm.md) - HOW the navigation and FSM subsystems work

## Interface Scope

This document defines the launch arguments, ROS topics, and ownership boundaries used by the integrated `auto_explore` package.

## ROS Topics

### External Sensor & Base Topics

| Topic | Type | Primary Owner | Purpose |
|---|---|---|---|
| `/map` | `nav_msgs/msg/OccupancyGrid` | SLAM Toolbox | Global map updates from SLAM |
| `/odom` | `nav_msgs/msg/Odometry` | Robot base (TurtleBot3) | Robot pose and velocity estimates |
| `/scan` | `sensor_msgs/msg/LaserScan` | LiDAR sensor | Obstacle and frontier sensing data |
| `/tf` | `tf2_msgs/msg/TFMessage` | TF2 broadcast (SLAM Toolbox) | Coordinate frame transformations |
| `/camera/image_raw` | `sensor_msgs/msg/Image` | Camera | Raw camera image stream |
| `/camera/camera_info` | `sensor_msgs/msg/CameraInfo` | Camera | Camera intrinsic calibration data |

### Mission Control Topics

| Topic | Type | Primary Owner | Purpose |
|---|---|---|---|
| `/states` | `std_msgs/msg/String` | Mission controller | FSM state publication (EXPLORE, DOCK, LAUNCH, END) |
| `/shoot_type` | `std_msgs/msg/String` | Mission controller | Shooter trigger mode (static, dynamic, or idle) |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Mission controller | Composite base velocity command |

### Marker Detection Topics

| Topic | Type | Primary Owner | Purpose |
|---|---|---|---|
| `/aruco/debug` | `std_msgs/msg/String` | Pose publisher | Marker pose payload and debug data |
| `/marker_detected` | `std_msgs/msg/Bool` | Pose publisher | Boolean signal indicating marker visibility |

### Internal Subsystem Topics

| Topic | Type | Primary Owner | Purpose |
|---|---|---|---|
| `/cmd_vel_nav` | `geometry_msgs/msg/Twist` | Exploration controller | Velocity commands from frontier-based navigation |
| `/cmd_vel_docking` | `geometry_msgs/msg/Twist` | Docking controller | Velocity commands from docking behavior |
| `/map_explored` | `std_msgs/msg/Bool` | Exploration controller | Frontier exploration completion signal |
| `/exploration_path` | `nav_msgs/msg/Path` | Exploration controller | Planned frontier-based path for visualization |
| `/dock_done` | `std_msgs/msg/Bool` | Docking controller | Dock cycle completion signal |
| `/shoot_done` | `std_msgs/msg/Bool` | Shooter controller | Shooter execution completion signal |

## Message Types

Topic type contracts above are the runtime reference and should be revalidated after interface changes.

Message type summary:
- `std_msgs/msg/String` - Text payloads (mission states, shooter modes, debug data)
- `std_msgs/msg/Bool` - Binary completion/status signals
- `geometry_msgs/msg/Twist` - Velocity commands (linear and angular components)
- `nav_msgs/msg/OccupancyGrid` - Occupancy map from SLAM
- `nav_msgs/msg/Odometry` - Pose and velocity estimates
- `nav_msgs/msg/Path` - Planned path visualization
- `sensor_msgs/msg/LaserScan` - LiDAR range data
- `sensor_msgs/msg/Image` - Raw camera image
- `sensor_msgs/msg/CameraInfo` - Camera calibration parameters
- `tf2_msgs/msg/TFMessage` - TF2 coordinate frame broadcasts

## Publish / Subscribe Ownership

**Exploration Controller:**
- Publishes: `/cmd_vel_nav`, `/map_explored`, `/exploration_path`
- Subscribes to: `/map`, `/odom`, `/scan`

**Mission Controller (FSM):**
- Publishes: `/states`, `/shoot_type`, `/cmd_vel` (arbitrates nav and docking velocities)
- Subscribes to: `/dock_done`, `/shoot_done`, `/map_explored`, `/marker_detected`, `/tf`, `/cmd_vel_nav`, `/cmd_vel_docking`

**Docking Controller:**
- Publishes: `/cmd_vel_docking`, `/dock_done`
- Subscribes to: `/odom`, `/tf`, `/states`

**Shooter Controller:**
- Publishes: `/shoot_done`
- Subscribes to: `/shoot_type`

**Pose Publisher (ArUco marker detection):**
- Publishes: `/aruco/debug`, `/marker_detected`
- Subscribes to: `/camera/image_raw`, `/camera/camera_info`

**SLAM Toolbox:**
- Publishes: `/map`, `/tf` (map↔odom transforms)
- Subscribes to: `/scan`

## Launch Arguments

### Top-level integrated launcher (`global_bringup.py`)

- `use_sim_time` - Use simulation clock if `true`; use system wall time if `false`
- `enable_slam` - Enable SLAM Toolbox mapping (default: `true`)
- `enable_rviz` - Enable RViz visualization (default: `true`)
- `slam_params_file` - Path to SLAM config YAML
- `enable_fsm` - Enable mission FSM (default: `true`)
- `enable_navigation` - Enable frontier exploration controller (default: `true`)
- `enable_markers` - Enable ArUco marker detection (default: `true`)
- `enable_pose_publisher` - Enable pose publisher node (default: `true`)
- `enable_docking` - Enable docking controller (default: `true`)
- `enable_shooter` - Enable shooter controller (default: `true`)
- `shooter_enable_hardware` - Enable physical GPIO actuation for shooter (default: `false`)

### Controller launcher (`global_controller_bringup.py`)

Includes all controller toggles plus shooter tuning arguments:

- `use_sim_time`
- `nav_params_file` - Path to navigation/exploration parameter YAML
- `enable_fsm`, `enable_navigation`, `enable_markers`, `enable_pose_publisher`, `enable_docking`, `enable_shooter`, `shooter_enable_hardware`
- `shooter_pigpiod_host` - Raspberry Pi hostname/IP running pigpiod (default: `localhost`)
- `shooter_pigpiod_port` - pigpiod port (default: `8888`)
- `shooter_ultrasonic_trigger_pin` - GPIO pin for ultrasonic trigger (default: `23`)
- `shooter_ultrasonic_echo_pin` - GPIO pin for ultrasonic echo (default: `24`)
- `shooter_ultrasonic_distance_threshold_m` - Fire distance threshold (default: `0.20` m)
- `shooter_ultrasonic_simulated_distance_m` - Simulated distance when hardware disabled (default: `0.15` m)
- `shooter_engage_profile` - Rack engagement profile: `mild`, `medium`, `strong` (default: `medium`)

### Navigation launcher (`nav_bringup.py`)

- `use_sim_time`
- `enable_slam`
- `enable_rviz`
- `slam_params_file`
- `slam_start_delay_sec` - Delay before SLAM start to stabilize TF/scan (default: `10.0` s)
- `rviz_start_delay_sec` - Delay before RViz start to let SLAM initialize (default: `10.0` s)

### Important Propagation Note

`global_bringup.py` is the integrated entrypoint, but shooter tuning arguments are declared in `global_controller_bringup.py`. If host/ultrasonic tuning is required, launch the controller bringup directly or update argument forwarding in `global_bringup.py`.

For simulation, use shorter delays: `slam_start_delay_sec:=2.0`, `rviz_start_delay_sec:=2.0`.

## Timing and Rates

### Launch-Time Delays

These delays prevent TF2 and sensor startup races:

| Delay Parameter | Gazebo Default | Real Robot Default | Purpose |
|---|---|---|---|
| `slam_start_delay_sec` | 2.0 s | 10.0 s | Wait for TF publishers and scan to stabilize before SLAM initialization |
| `rviz_start_delay_sec` | 2.0 s | 10.0 s | Wait for SLAM to publish map before RViz starts |

**Rationale:** Gazebo clock advances instantly; real robots have slower hardware initialization.

### Control Loop Rates

| Node | Rate | Purpose |
|---|---|---|
| Exploration Controller | 10 Hz | Path planning and velocity command computation |
| Mission Controller (FSM) | 10 Hz | State machine and velocity arbitration |
| Docking Controller | 10 Hz | Docking sequence and marker tracking |
| Shooter Controller | 10 Hz | Trigger logic and status publishing |
| Pose Publisher | 30 Hz (camera dependent) | ArUco marker detection and pose estimation |
| SLAM Toolbox | 25-50 Hz | Map updates and TF broadcasting |

### Topic Publishing Frequencies

| Topic | Frequency | QoS Profile | Notes |
|---|---|---|---|
| `/map` | 1-5 Hz | Reliable | Updated when new scans are processed |
| `/odom` | 20-30 Hz | Best-effort (sensor QoS) | Matches LiDAR or encoder rate |
| `/scan` | 10-20 Hz | Best-effort (sensor QoS) | LiDAR scan rate |
| `/tf` | 25+ Hz | Varies | TF2 broadcasts at sensor rates |
| `/states` | 10 Hz | Reliable | FSM state transitions |
| `/cmd_vel`, `/cmd_vel_nav`, `/cmd_vel_docking` | 10 Hz | Reliable | Controller outputs |
| `/marker_detected`, `/dock_done`, `/shoot_done` | Event-driven | Reliable | Published on state change |

## Error and Fallback Behavior

### Missing `/map` (SLAM not running or failed)
- **Behavior:** Exploration controller halts, publishes zero velocity on `/cmd_vel_nav`
- **FSM Impact:** Remains in EXPLORE; `/map_explored` stays `false`
- **Recovery:** Restart SLAM Toolbox; verify `/map` topic appears within 15 seconds
- **User Action:** Check SLAM logs; confirm `/scan` is being published; verify LiDAR connectivity

### Missing `/odom` (Robot odometry unavailable)
- **Behavior:** Docking controller and exploration controller cannot localize; publish zero velocity
- **FSM Impact:** FSM cannot transition to DOCK; mission stalls
- **Recovery:** Restart TurtleBot3 bringup; verify robot base is running
- **User Action:** Check if `robot.launch.py` succeeded; verify `/tf` and `/odom` topics exist

### Missing `/scan` (LiDAR offline)
- **Behavior:** Exploration controller cannot detect obstacles; may plan unsafe paths
- **FSM Impact:** FSM remains in EXPLORE with zero velocity
- **Recovery:** Check LiDAR USB connection; restart LiDAR node; verify `/scan` reappears
- **User Action:** `ros2 node list | grep scan`; check LiDAR power and USB cable

### Missing `/camera/image_raw` or `/camera/camera_info`
- **Behavior:** Pose publisher fails silently; `/marker_detected` stays `false`
- **FSM Impact:** FSM never transitions from EXPLORE to DOCK
- **Recovery:** Restart camera node; verify topics under 5 seconds
- **User Action:** Check camera USB connection; run `ros2 run camera_ros camera_node` manually if needed

### Marker detection failure (marker not visible or poor lighting)
- **Behavior:** Pose publisher publishes `false` on `/marker_detected`
- **FSM Impact:** Mission loops in EXPLORE indefinitely
- **Recovery:** Adjust lighting; ensure ArUco marker is visible to camera; check marker size in launch args (`marker_size_m: 0.053`)
- **User Action:** Verify marker orientation; test with `ros2 run cv_bridge cv_bridge_demo_color`

### Docking controller failure
- **Behavior:** Robot cannot reach docking marker; `/dock_done` stays `false` for > 20s timeout
- **FSM Impact:** FSM times out after `dock_cycle_timeout_sec` (20s default); republishes state as DOCK
- **Recovery:** Disable docking (`enable_docking:=false`) to skip DOCK state; adjust timeout parameter
- **User Action:** Check docking marker visibility; verify robot can navigate to marker pose

### Shooter hardware unavailable
- **Behavior:** With `shooter_enable_hardware:=false`, shooter uses simulated distance; fires at threshold
- **FSM Impact:** Mission progresses normally; only firing is simulated
- **Recovery:** Set `shooter_enable_hardware:=true` to enable hardware GPIO; verify Raspberry Pi running `pigpiod`
- **User Action:** SSH to Pi; run `sudo pigpiod`; verify GPIO pins accessible; test with `pigs servo <pin> <value>`

## Interface Change Rules

### When to Update This Document

Update this document **before or immediately after** any of the following changes:

1. **Topic Addition/Removal/Rename:**
   - Add new row to appropriate ROS Topics section
   - Update Publish/Subscribe Ownership section
   - Update subsystem-nav-fsm.md and software-firmware-development.md references
   - Example: Adding `/base_status` topic → add to External Sensor Topics table

2. **Message Type Change:**
   - Example: Changing `/shoot_type` from `std_msgs/msg/String` to `std_msgs/msg/Int32`
   - Update ROS Topics table, Message Types section, and Publish/Subscribe Ownership
   - Verify all subscribers/publishers in code match new type

3. **Launch Argument Addition/Removal:**
   - Add/remove from appropriate launcher section
   - Document default value and purpose
   - Update software-firmware-development.md launch command examples
   - Example: Adding `exploration_max_iterations` → add to "Top-level integrated launcher"

4. **Control Loop Rate Change:**
   - Update Timing and Rates table
   - Document rationale in table notes
   - Verify message ordering and QoS profiles remain compatible

5. **Error Handling or Fallback Logic Change:**
   - Update corresponding entry in Error and Fallback Behavior section
   - Document new recovery procedures
   - Update troubleshooting guide in software-firmware-development.md
