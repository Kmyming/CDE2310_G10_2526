# Note: Full integrated marker detection coming soon.
# Setup Instructions

## Prerequisites

- ROS2 - Humble
- Slam Toolbox
- Turtlebot3 Package
- TurtleBot3 workspace (`turtlebot3_ws`)

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

### Launch Sequences

#### Gazebo Simulation

**Terminal 1:** Launch default Gazebo world

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

**Terminal 2:** Launch auto_explore mission control system

```bash
ros2 launch auto_explore global_bringup.py \
  use_sim_time:=true \
  enable_slam:=true \
  enable_rviz:=true \
  enable_markers:=true
```

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
  enable_markers:=true
```

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
enable_markers:=true|false     # Enable ArUco marker detection
```

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

---

## LEGACY: Manual Launch (For Reference)

### Installation (Legacy - autonomous_exploration package)

If you want to use the old `autonomous_exploration` package:

```bash
cd ~/turtlebot3_ws/src
git clone https://github.com/Kmyming/CDE2310_G10_2526.git autonomous_exploration
cd ~/turtlebot3_ws
colcon build --packages-select autonomous_exploration
source install/setup.bash
```

Verify:
```bash
ros2 pkg list | grep autonomous_exploration
```

### Manual Component Launch

If you prefer to run components separately:

1. **Launch the Map Node (SLAM):**

```bash
ros2 launch slam_toolbox online_async_launch.py
```

2. **Launch the Gazebo simulation environment:**

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

3. **View the environment map in RViz:**

```bash
rviz2 -d ~/turtlebot3_ws/src/turtlebot3/turtlebot3_cartographer/rviz/tb3_cartographer.rviz
```

4. **Run the autonomous exploration package:**

```bash
ros2 run autonomous_exploration control
```