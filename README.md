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
git clone https://github.com/Kmyming/CDE2310_G10_2526.git autonomous_exploration
cd ~/turtlebot3_ws
```

2. **Build the package using colcon:**

```bash
colcon build --packages-select autonomous_exploration
source install/setup.bash
```

3. **Verify the build was successful:**

```bash
ros2 pkg list | grep autonomous_exploration
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

### Launch the System

Use the provided launch wrapper script:

```bash
# Gazebo simulation environment (Terminal 1 - optional, run separately)
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# Launch auto_explore system (Terminal 2)
# Use the wrapper script to properly set up the environment
cd ~/turtlebot3_ws/src/CDE2310_G10_2526/remote_laptop_src
./launch_auto_explore.sh global_bringup.py use_sim_time:=true enable_markers:=true
```

This launches:
- SLAM Toolbox (mapping)
- RViz (visualization)
- FSM Controller (mission state machine)
- Exploration Controller (frontier-based navigation)
- ArUco Marker Detection (pose publisher)
- Marker Logger (logging marker detections to ./logs/)

### Launch Command Options

```bash
# Default (everything enabled)
./launch_auto_explore.sh global_bringup.py use_sim_time:=true

# Without markers
./launch_auto_explore.sh global_bringup.py use_sim_time:=true enable_markers:=false

# Without RViz visualization
./launch_auto_explore.sh global_bringup.py use_sim_time:=true enable_rviz:=false

# Real robot (disables simulation clock)
./launch_auto_explore.sh global_bringup.py use_sim_time:=false

# View available launch arguments
./launch_auto_explore.sh global_bringup.py --show-args
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