# TurtleBot3 Autonomous Exploration & Mission Control System

## Overview

This repository contains a complete ROS2-based autonomous exploration system for TurtleBot3. The robot autonomously explores environments, detects ArUco markers, performs docking, and executes payload delivery—all orchestrated by a finite state machine.

**Current Status:** ✓ System operational - all components tested and verified

---

## Prerequisites

- **ROS2:** Humble
- **Packages:** slam_toolbox, turtlebot3, turtlebot3_gazebo, opencv-python
- **Hardware:** TurtleBot3 Burger (with camera sensor)
- **Workspace:** `turtlebot3_ws`

## Installation

1. **Clone this repository into your TurtleBot3 workspace:**

```bash
cd ~/turtlebot3_ws/src
git clone https://github.com/Kmyming/CDE2310_G10_2526.git CDE2310_G10_2526
cd ~/turtlebot3_ws
```

2. **Build the auto_explore package using colcon:**

```bash
colcon build --packages-select auto_explore
source install/setup.bash
```

3. **Verify the build was successful:**

```bash
ros2 pkg list | grep auto_explore
```

Expected output:
```
auto_explore
```


# How to Run

## NEW: Independent Auto-Explore System (Recommended)

**Package Name:** `auto_explore` (completely independent mission control system)

### Setup

Build the `auto_explore` package:

```bash
cd ~/turtlebot3_ws
colcon build --packages-select auto_explore
source install/setup.bash
```

### Launch Sequences (Verified)

#### Gazebo Simulation

`global_bringup.py` is the unified command for the **mission stack** (SLAM + controllers + markers), but Gazebo must still be started separately.

**Terminal 1 (Gazebo):**

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

**Terminal 2 (Unified mission stack):**

```bash
ros2 launch auto_explore global_bringup.py \
  use_sim_time:=true \
  enable_slam:=true \
  enable_rviz:=false \
  enable_fsm:=true \
  enable_navigation:=true \
  enable_markers:=true \
  enable_marker_logger:=true \
  enable_docking:=false \
  enable_shooter:=false
```

This command is validated against current launch arguments in `auto_explore/launch/global_bringup.py`.

#### Physical TurtleBot3 Robot

**Terminal 1:** Run TurtleBot3 bringup

```bash
# If 'rosbu' alias is set up:
rosbu

# Otherwise:
ros2 launch turtlebot3_bringup robot.launch.py
```

**Terminal 2:** Launch auto_explore mission control system

```bash
ros2 launch auto_explore global_bringup.py \
  use_sim_time:=false \
  enable_slam:=true \
  enable_rviz:=true \
  enable_markers:=true \
  enable_docking:=true \
  enable_shooter:=true \
  shooter_enable_hardware:=true
```

**Important:** copy the command exactly as plain text into bash. Do **not** include Markdown link syntax like `[global_bringup.py](...)`, which causes shell parsing errors.

### Launch Components

This launches:
- **SLAM Toolbox** (mapping) - enabled with `enable_slam:=true`
- **RViz** (visualization) - enabled with `enable_rviz:=true`
- **FSM Controller** (mission state machine)
- **Exploration Controller** (frontier-based autonomous navigation)
- **ArUco Marker Detection** (pose publisher) - enabled with `enable_markers:=true`
- **Marker Logger** (logging marker detections to `./logs/`)

### Launch Arguments

```bash
use_sim_time:=true|false      # Use Gazebo time (true) or real time (false)
enable_slam:=true|false        # Enable SLAM Toolbox mapping
enable_rviz:=true|false        # Enable RViz visualization
enable_fsm:=true|false         # Enable mission FSM
enable_navigation:=true|false  # Enable frontier exploration controller
enable_markers:=true|false     # Enable ArUco marker detection
enable_marker_logger:=true|false # Enable ArUco logger
enable_docking:=true|false     # Enable docking controller
enable_shooter:=true|false     # Enable shooter controller
shooter_enable_hardware:=false|true # GPIO actuation (physical robot only)
```

Recommended values:
- Gazebo/simulation: `shooter_enable_hardware:=false`
- Real robot hardware: `shooter_enable_hardware:=true`

### Architecture

The `auto_explore` package contains:
- **global_bringup.py** - Entry point with component control flags
- **nav_bringup.py** - Navigation infrastructure (SLAM, RViz)
- **global_controller_bringup.py** - Mission logic (FSM, exploration, markers)
- **mission_controller.py** - FSM state machine orchestration
- **exploration_controller.py** - Frontier-based autonomous exploration
- **pose_publisher.py** - ArUco marker detection
- **pose_subscriber.py** - Marker logging with rolling buffer
- **config/params.yaml** - Local exploration tuning parameters

### Subsystem Test Instructions

Use these tests to validate each subsystem independently after sourcing the workspace.

#### 1) Package + Launch Interface Sanity

```bash
ros2 pkg list | grep auto_explore
ros2 launch auto_explore global_bringup.py --show-args
ros2 pkg executables auto_explore
```

Expected: package is discoverable, all launch args listed, and executables include `mission_controller`, `exploration_controller`, `pose_publisher`, `pose_subscriber`, `docking_controller`, `shooter_controller`.

#### 2) Navigation Infrastructure (SLAM/RViz)

```bash
ros2 launch auto_explore nav_bringup.py use_sim_time:=true enable_slam:=true enable_rviz:=false
```

Check in another terminal:

```bash
ros2 topic list | grep -E '^/map$|^/map_metadata$'
```

Expected: `/map` is available and updating.

#### 3) FSM Only

```bash
ros2 launch auto_explore global_controller_bringup.py use_sim_time:=true \
  enable_fsm:=true enable_navigation:=false enable_markers:=false \
  enable_marker_logger:=false enable_docking:=false enable_shooter:=false
```

Check:

```bash
ros2 topic echo /states
```

Expected: FSM publishes `EXPLORE` on startup.

#### 4) Exploration Controller Only

```bash
ros2 launch auto_explore global_controller_bringup.py use_sim_time:=true \
  enable_fsm:=false enable_navigation:=true enable_markers:=false \
  enable_marker_logger:=false enable_docking:=false enable_shooter:=false
```

Check:

```bash
ros2 topic hz /cmd_vel
ros2 topic echo /map_explored
```

Expected: `/cmd_vel` publishes while navigating; `/map_explored` eventually becomes true.

#### 5) Marker Detection + Logger

```bash
ros2 launch auto_explore global_controller_bringup.py use_sim_time:=true \
  enable_fsm:=false enable_navigation:=false enable_markers:=true \
  enable_marker_logger:=true enable_docking:=false enable_shooter:=false
```

Check:

```bash
ros2 topic echo /aruco/debug
```

Expected: heartbeat JSON plus marker JSON when marker is in view.

#### 6) Docking Controller

```bash
ros2 launch auto_explore global_controller_bringup.py use_sim_time:=true \
  enable_fsm:=false enable_navigation:=false enable_markers:=false \
  enable_marker_logger:=false enable_docking:=true enable_shooter:=false
```

Check:

```bash
ros2 topic info /cmd_vel_docking
ros2 topic info /dock_done
```

Expected: docking topics are present; node is alive.

#### 7) Shooter Controller

Simulation-safe launch:

```bash
ros2 launch auto_explore global_controller_bringup.py use_sim_time:=true \
  enable_fsm:=false enable_navigation:=false enable_markers:=false \
  enable_marker_logger:=false enable_docking:=false enable_shooter:=true \
  shooter_enable_hardware:=false
```

Expected: shooter node starts without GPIO access errors.

#### 8) Full Smoke Test

```bash
ros2 launch auto_explore global_bringup.py \
  use_sim_time:=true enable_slam:=true enable_rviz:=false \
  enable_fsm:=true enable_navigation:=true enable_markers:=true \
  enable_marker_logger:=true enable_docking:=false enable_shooter:=false
```

Checks:

```bash
ros2 topic list | grep -E '^/states$|^/aruco/debug$|^/cmd_vel$|^/map$|^/odom$'
```

Expected: all critical topics are present and active.

---

## ⚙️ SLAM Optimization - Required Configuration

**⚠️ IMPORTANT:** All team members must update the SLAM Toolbox parameters to improve map responsiveness and accuracy. This is a required setup step before running any autonomous exploration missions.

### Update SLAM Mapper Parameters

Navigate to the SLAM Toolbox configuration directory and update the `mapper_params_online_async.yaml` file:

```bash
# Edit the configuration file
nano /opt/ros/humble/share/slam_toolbox/config/mapper_params_online_async.yaml
```

Apply the following parameter changes to improve SLAM efficiency and map responsiveness:

```yaml
slam_toolbox:
    ros__parameters:
    
    solver_plugin: solver_plugins::CeresSolver
    ceres_linear_solver: SPARSE_NORMAL_CHOLESKY
    ceres_preconditioner: SCHUR_JACOBI
    ceres_trust_strategy: LEVENBERG_MARQUARDT
    ceres_dogleg_type: TRADITIONAL_DOGLEG
    ceres_loss_function: None

    odom_frame: odom
    map_frame: map
    base_frame: base_footprint
    scan_topic: /scan
    use_map_saver: true
    mode: mapping

    debug_logging: false
    throttle_scans: 1
    transform_publish_period: 0.02
    map_update_interval: 1.0        # was 5.0 - faster map updates
    resolution: 0.05
    min_laser_range: 0.12           # was 0.0 - match LiDAR's (LDS-02) actual min range
    max_laser_range: 3.5            # was 20.0 - match LiDAR's (LDS-02) actual max range
    minimum_time_interval: 0.2      # was 0.5 - process scans more frequently
    transform_timeout: 0.2
    tf_buffer_duration: 30.
    stack_size_to_use: 40000000
    enable_interactive_mode: true

    use_scan_matching: true
    use_scan_barycenter: true
    minimum_travel_distance: 0.2    # was 0.5 - update after smaller movements
    minimum_travel_heading: 0.2     # was 0.5 - update after smaller rotations
    scan_buffer_size: 10
    scan_buffer_maximum_scan_distance: 3.5  # match max_laser_range
    link_match_minimum_response_fine: 0.1  
    link_scan_maximum_distance: 1.5
    loop_search_maximum_distance: 3.0
    do_loop_closing: true 
    loop_match_minimum_chain_size: 10           
    loop_match_maximum_variance_coarse: 3.0  
    loop_match_minimum_response_coarse: 0.35    
    loop_match_minimum_response_fine: 0.45

    correlation_search_space_dimension: 0.5
    correlation_search_space_resolution: 0.01
    correlation_search_space_smear_deviation: 0.1 

    loop_search_space_dimension: 8.0
    loop_search_space_resolution: 0.05
    loop_search_space_smear_deviation: 0.03

    distance_variance_penalty: 0.5      
    angle_variance_penalty: 1.0    
    fine_search_angle_offset: 0.00349     
    coarse_search_angle_offset: 0.349   
    coarse_angle_resolution: 0.0349        
    minimum_angle_penalty: 0.9
    minimum_distance_penalty: 0.5
    use_response_expansion: true
    min_pass_through: 2
    occupancy_threshold: 0.1
```

### Key Changes Summary

The critical improvements made:
- **`map_update_interval`**: Reduced from 5.0 to 1.0 seconds for faster map updates
- **`min_laser_range`**: Set to 0.12 to match LiDAR (LDS-02) actual minimum range
- **`max_laser_range`**: Set to 3.5 to match LiDAR (LDS-02) actual maximum range
- **`minimum_time_interval`**: Reduced from 0.5 to 0.2 for more frequent scan processing
- **`minimum_travel_distance`**: Reduced from 0.5 to 0.2 for updates after smaller movements
- **`minimum_travel_heading`**: Reduced from 0.5 to 0.2 for updates after smaller rotations

These changes ensure the map updates more responsively as the robot explores, resulting in better real-time mapping performance and more accurate frontier detection for autonomous exploration.

---

## 📊 RViz Configuration Update - Required

**⚠️ IMPORTANT:** All team members must update their local `tb3_cartographer.rviz` file. This ensures everyone has the same visualization setup including the exploration path display.

### Update RViz Configuration

**Step 1:** Backup your current config
```bash
cp ~/turtlebot3_ws/src/turtlebot3/turtlebot3_cartographer/rviz/tb3_cartographer.rviz ~/tb3_cartographer.rviz.backup
```

**Step 2:** Replace the entire contents of `tb3_cartographer.rviz` with this configuration

Open the file:
```bash
nano ~/turtlebot3_ws/src/turtlebot3/turtlebot3_cartographer/rviz/tb3_cartographer.rviz
```

Delete all existing content and paste this entire configuration:

```yaml
Panels:
  - Class: rviz_common/Displays
    Help Height: 78
    Name: Displays
    Property Tree Widget:
      Expanded:
        - /Global Options1
        - /LaserScan1/Topic1
      Splitter Ratio: 0.3916349709033966
    Tree Height: 347
  - Class: rviz_common/Selection
    Name: Selection
  - Class: rviz_common/Tool Properties
    Expanded:
      - /Publish Point1
      - /2D Pose Estimate1
    Name: Tool Properties
    Splitter Ratio: 0.5886790156364441
  - Class: rviz_common/Views
    Expanded:
      - /Current View1
    Name: Views
    Splitter Ratio: 0.5
Visualization Manager:
  Class: ""
  Displays:
    - Alpha: 0.5
      Cell Size: 1
      Class: rviz_default_plugins/Grid
      Color: 160; 160; 164
      Enabled: true
      Line Style:
        Line Width: 0.029999999329447746
        Value: Lines
      Name: Grid
      Normal Cell Count: 0
      Offset:
        X: 0
        Y: 0
        Z: 0
      Plane: XY
      Plane Cell Count: 10
      Reference Frame: <Fixed Frame>
      Value: true
    - Class: rviz_default_plugins/TF
      Enabled: true
      Frame Timeout: 15
      Frames:
        All Enabled: false
        base_footprint:
          Value: false
        base_link:
          Value: true
        base_scan:
          Value: false
        caster_back_link:
          Value: false
        imu_link:
          Value: false
        map:
          Value: false
        odom:
          Value: false
        wheel_left_link:
          Value: false
        wheel_right_link:
          Value: false
      Marker Scale: 1
      Name: TF
      Show Arrows: true
      Show Axes: true
      Show Names: true
      Tree:
        map:
          odom:
            base_footprint:
              base_link:
                base_scan:
                  {}
                caster_back_link:
                  {}
                imu_link:
                  {}
                wheel_left_link:
                  {}
                wheel_right_link:
                  {}
      Update Interval: 0
      Value: true
    - Alpha: 1
      Autocompute Intensity Bounds: true
      Autocompute Value Bounds:
        Max Value: 10
        Min Value: -10
        Value: true
      Axis: Z
      Channel Name: intensity
      Class: rviz_default_plugins/LaserScan
      Color: 255; 255; 255
      Color Transformer: Intensity
      Decay Time: 0
      Enabled: true
      Invert Rainbow: false
      Max Color: 255; 255; 255
      Max Intensity: 4439
      Min Color: 0; 0; 0
      Min Intensity: 105
      Name: LaserScan
      Position Transformer: XYZ
      Selectable: true
      Size (Pixels): 3
      Size (m): 0.019999999552965164
      Style: Boxes
      Topic:
        Depth: 50
        Durability Policy: Volatile
        Filter size: 10
        History Policy: Keep Last
        Reliability Policy: Best Effort 
        Value: /scan
      Use Fixed Frame: true
      Use rainbow: true
      Value: true
    - Angle Tolerance: 0.10000000149011612
      Class: rviz_default_plugins/Odometry
      Covariance:
        Orientation:
          Alpha: 0.5
          Color: 255; 255; 127
          Color Style: Unique
          Frame: Local
          Offset: 1
          Scale: 1
          Value: true
        Position:
          Alpha: 0.30000001192092896
          Color: 204; 51; 204
          Scale: 1
          Value: true
        Value: false
      Enabled: false
      Keep: 100
      Name: Odometry
      Position Tolerance: 0.10000000149011612
      Shape:
        Alpha: 1
        Axes Length: 1
        Axes Radius: 0.10000000149011612
        Color: 255; 25; 0
        Head Length: 0.30000001192092896
        Head Radius: 0.10000000149011612
        Shaft Length: 1
        Shaft Radius: 0.05000000074505806
        Value: Arrow
      Topic:
        Depth: 5
        Durability Policy: Volatile
        Filter size: 10
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /odom
      Value: false
    - Alpha: 0.699999988079071
      Class: rviz_default_plugins/Map
      Color Scheme: map
      Draw Behind: false
      Enabled: true
      Name: Map
      Topic:
        Depth: 5
        Durability Policy: Transient Local
        Filter size: 10
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /map
      Update Topic:
        Depth: 5
        Durability Policy: Transient Local
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /map_updates
      Use Timestamp: false
      Value: true
    - Class: rviz_common/Group
      Displays:
        - Class: rviz_common/Group
          Displays:
            - Alpha: 0.699999988079071
              Class: rviz_default_plugins/Map
              Color Scheme: costmap
              Draw Behind: true
              Enabled: true
              Name: Map
              Topic:
                Depth: 5
                Durability Policy: Volatile
                Filter size: 10
                History Policy: Keep Last
                Reliability Policy: Reliable
                Value: /global_costmap/costmap
              Update Topic:
                Depth: 5
                Durability Policy: Volatile
                History Policy: Keep Last
                Reliability Policy: Reliable
                Value: /global_costmap/costmap_updates
              Use Timestamp: false
              Value: true
            - Alpha: 1
              Buffer Length: 1
              Class: rviz_default_plugins/Path
              Color: 255; 0; 0
              Enabled: true
              Head Diameter: 0.30000001192092896
              Head Length: 0.20000000298023224
              Length: 0.30000001192092896
              Line Style: Lines
              Line Width: 0.029999999329447746
              Name: Path
              Offset:
                X: 0
                Y: 0
                Z: 0
              Pose Color: 255; 85; 255
              Pose Style: None
              Radius: 0.029999999329447746
              Shaft Diameter: 0.10000000149011612
              Shaft Length: 0.10000000149011612
              Topic:
                Depth: 5
                Durability Policy: Volatile
                Filter size: 10
                History Policy: Keep Last
                Reliability Policy: Reliable
                Value: /global_plan
              Value: true
          Enabled: true
          Name: Global Map
        - Class: rviz_common/Group
          Displays:
            - Alpha: 1
              Class: rviz_default_plugins/Polygon
              Color: 25; 255; 0
              Enabled: true
              Name: Polygon
              Topic:
                Depth: 5
                Durability Policy: Volatile
                Filter size: 10
                History Policy: Keep Last
                Reliability Policy: Reliable
                Value: /local_costmap/footprint
              Value: true
            - Alpha: 0.699999988079071
              Class: rviz_default_plugins/Map
              Color Scheme: costmap
              Draw Behind: false
              Enabled: true
              Name: Map
              Topic:
                Depth: 5
                Durability Policy: Volatile
                Filter size: 10
                History Policy: Keep Last
                Reliability Policy: Reliable
                Value: /local_costmap/costmap
              Update Topic:
                Depth: 5
                Durability Policy: Volatile
                History Policy: Keep Last
                Reliability Policy: Reliable
                Value: /local_costmap/costmap_updates
              Use Timestamp: false
              Value: true
            - Alpha: 1
              Buffer Length: 1
              Class: rviz_default_plugins/Path
              Color: 255; 255; 0
              Enabled: true
              Head Diameter: 0.30000001192092896
              Head Length: 0.20000000298023224
              Length: 0.30000001192092896
              Line Style: Lines
              Line Width: 0.029999999329447746
              Name: Path
              Offset:
                X: 0
                Y: 0
                Z: 0
              Pose Color: 255; 85; 255
              Pose Style: None
              Radius: 0.029999999329447746
              Shaft Diameter: 0.10000000149011612
              Shaft Length: 0.10000000149011612
              Topic:
                Depth: 5
                Durability Policy: Volatile
                Filter size: 10
                History Policy: Keep Last
                Reliability Policy: Reliable
                Value: /local_plan
              Value: true
          Enabled: true
          Name: Local Map
        - Alpha: 1
          Arrow Length: 0.05000000074505806
          Axes Length: 0.30000001192092896
          Axes Radius: 0.009999999776482582
          Class: rviz_default_plugins/PoseArray
          Color: 0; 192; 0
          Enabled: true
          Head Length: 0.07000000029802322
          Head Radius: 0.029999999329447746
          Name: PoseArray
          Shaft Length: 0.23000000417232513
          Shaft Radius: 0.009999999776482582
          Shape: Arrow (Flat)
          Topic:
            Depth: 5
            Durability Policy: Volatile
            Filter size: 10
            History Policy: Keep Last
            Reliability Policy: Reliable
            Value: /particlecloud
          Value: true
      Enabled: false
      Name: Navigation
    - Class: rviz_common/Group
      Displays:
        - Alpha: 1
          Autocompute Intensity Bounds: true
          Autocompute Value Bounds:
            Max Value: 0.18203988671302795
            Min Value: 0.18195410072803497
            Value: true
          Axis: Z
          Channel Name: intensity
          Class: rviz_default_plugins/PointCloud2
          Color: 0; 255; 0
          Color Transformer: FlatColor
          Decay Time: 0
          Enabled: true
          Invert Rainbow: false
          Max Color: 255; 255; 255
          Max Intensity: 4096
          Min Color: 0; 0; 0
          Min Intensity: 0
          Name: scan_matched_points2
          Position Transformer: XYZ
          Selectable: true
          Size (Pixels): 3
          Size (m): 0.009999999776482582
          Style: Boxes
          Topic:
            Depth: 5
            Durability Policy: Volatile
            Filter size: 10
            History Policy: Keep Last
            Reliability Policy: Reliable
            Value: /scan_matched_points2
          Use Fixed Frame: true
          Use rainbow: true
          Value: true
        - Class: rviz_default_plugins/MarkerArray
          Enabled: false
          Name: Trajectories
          Namespaces:
            {}
          Topic:
            Depth: 5
            Durability Policy: Volatile
            History Policy: Keep Last
            Reliability Policy: Reliable
            Value: /trajectory_node_list
          Value: false
        - Class: rviz_default_plugins/MarkerArray
          Enabled: false
          Name: Constraints
          Namespaces:
            {}
          Topic:
            Depth: 5
            Durability Policy: Volatile
            History Policy: Keep Last
            Reliability Policy: Reliable
            Value: /constraint_list
          Value: false
        - Class: rviz_default_plugins/MarkerArray
          Enabled: false
          Name: Landmark Poses
          Namespaces:
            {}
          Topic:
            Depth: 5
            Durability Policy: Volatile
            History Policy: Keep Last
            Reliability Policy: Reliable
            Value: /landmark_poses_list
          Value: false
      Enabled: true
      Name: Cartographer
    - Alpha: 1
      Buffer Length: 1
      Class: rviz_default_plugins/Path
      Color: 0; 255; 255
      Enabled: true
      Head Diameter: 0.30000001192092896
      Head Length: 0.20000000298023224
      Length: 0.30000001192092896
      Line Style: Lines
      Line Width: 0.05000000074505806
      Name: Exploration Path
      Offset:
        X: 0
        Y: 0
        Z: 0
      Pose Color: 255; 85; 255
      Pose Style: None
      Radius: 0.029999999329447746
      Shaft Diameter: 0.10000000149011612
      Shaft Length: 0.10000000149011612
      Topic:
        Depth: 5
        Durability Policy: Volatile
        Filter size: 10
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /exploration_path
      Value: true
  Enabled: true
  Global Options:
    Background Color: 48; 48; 48
    Fixed Frame: map
    Frame Rate: 10
  Name: root
  Tools:
    - Class: rviz_default_plugins/MoveCamera
    - Class: rviz_default_plugins/Select
    - Class: rviz_default_plugins/FocusCamera
    - Class: rviz_default_plugins/Measure
      Line color: 128; 128; 0
    - Class: rviz_default_plugins/SetGoal
      Topic:
        Depth: 5
        Durability Policy: Volatile
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /move_base_simple/goal
    - Class: rviz_default_plugins/PublishPoint
      Single click: true
      Topic:
        Depth: 5
        Durability Policy: Volatile
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /clicked_point
    - Class: rviz_default_plugins/SetInitialPose
      Covariance x: 0.25
      Covariance y: 0.25
      Covariance yaw: 0.06853891909122467
      Topic:
        Depth: 5
        Durability Policy: Volatile
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: initialpose
  Transformation:
    Current:
      Class: rviz_default_plugins/TF
  Value: true
  Views:
    Current:
      Angle: 0
      Class: rviz_default_plugins/TopDownOrtho
      Enable Stereo Rendering:
        Stereo Eye Separation: 0.05999999865889549
        Stereo Focal Distance: 1
        Swap Stereo Eyes: false
        Value: false
      Invert Z Axis: false
      Name: Current View
      Near Clip Distance: 0.009999999776482582
      Scale: 119.26066589355469
      Target Frame: <Fixed Frame>
      Value: TopDownOrtho (rviz_default_plugins)
      X: 0.0023878198117017746
      Y: -0.17037495970726013
    Saved: ~
Window Geometry:
  Displays:
    collapsed: false
  Height: 576
  Hide Left Dock: false
  Hide Right Dock: true
  QMainWindow State: 000000ff00000000fd00000004000000000000017a000001e6fc0200000008fb0000001200530065006c0065006300740069006f006e00000001e10000009b0000005c00fffffffb0000001e0054006f006f006c002000500072006f007000650072007400690065007302000001ed000001df00000185000000a3fb000000120056006900650077007300200054006f006f02000001df000002110000018500000122fb000000200054006f006f006c002000500072006f0070006500720074006900650073003203000002880000011d000002210000017afb000000100044006900730070006c006100790073010000003d000001e6000000c900fffffffb0000002000730065006c0065006300740069006f006e00200062007500660066006500720200000138000000aa0000023a00000294fb00000014005700690064006500530074006500720065006f02000000e6000000d2000003ee0000030bfb0000000c004b0069006e0065006300740200000186000001060000030c00000261000000010000010f00000236fc0200000003fb0000001e0054006f006f006c002000500072006f00700065007200740069006500730100000041000000780000000000000000fb0000000a00560069006500770073000000003d00000236000000a400fffffffb0000001200530065006c0065006300740069006f006e010000025a000000b200000000000000000000000200000490000000a9fc0100000001fb0000000a00560069006500770073030000004e00000080000002e10000019700000003000004420000003efc0100000002fb0000000800540069006d00650100000000000004420000000000000000fb0000000800540069006d00650100000000000004500000000000000000000002db000001e600000004000000040000000800000008fc0000000100000002000000010000000a0054006f006f006c00730100000000ffffffff0000000000000000
  Selection:
    collapsed: false
  Tool Properties:
    collapsed: false
  Views:
    collapsed: true
  Width: 1115
  X: 164
  Y: 106
```

**Step 3:** Save and exit (Ctrl+O, Enter, Ctrl+X)

### What This Configuration Includes

✅ **Exploration Path Visualization** - Cyan path showing frontier navigation in real-time  
✅ **SLAM Displays** - Cartographer scan matching and point clouds  
✅ **Navigation Displays** - Global/local costmaps and planned paths  
✅ **Sensor Data** - LaserScan and odometry visualization  
✅ **Transform Tree** - Robot frame hierarchy visualization  

### Verify It Works

```bash
jrviz2
# or
rviz2 -d ~/turtlebot3_ws/src/turtlebot3/turtlebot3_cartographer/rviz/tb3_cartographer.rviz
```

You should now see all displays including the **cyan Exploration Path** in real-time!