# ROS2-FrontierBaseExplorationForAutonomousRobot
Our autonomous ground vehicle uses Frontier Based exploration to navigate and map unknown environments. Equipped with sensors, it can avoid obstacles and make real-time decisions. It has potential applications in search and rescue, agriculture, and logistics, and represents an important step forward in autonomous ground vehicle development.

This project utilizes the **Frontier-Based Exploration** algorithm for autonomous exploration. The project employs **DFS** for grouping boundary points, **A*** for finding the shortest path, **B-Spline** for smoothing path curvature, and **Pure Pursuit** for path following, along with other obstacle avoidance techniques. The combination of these techniques aims to provide a sophisticated, efficient, and reliable solution for autonomous ground vehicle exploration in a wide range of applications.


![Screenshot_1](https://user-images.githubusercontent.com/87595266/218670694-e53bb1c4-fff2-42e9-9b9e-62b298da7df.png)


# Youtube Project Presentation Video & Demo

https://youtu.be/UxCZAU9ZZoc

# Update Version V1.1 - 26.02.2023

https://youtu.be/_1vtmFuhl9Y

- The exploration algorithm has been optimized.
- Robot decision algorithm has been changed. Watch the video for detailed information.
- Thread structure has been added to the exploration algorithm.


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

1. **Launch the Map Node (SLAM):**

```bash
ros2 launch slam_toolbox online_async_launch.py
```

2. **Launch the Gazebo simulation environment:**

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

3. **View the environment map in RViz** (update the path to your RViz config):

```bash
rviz2 -d ~/turtlebot3_ws/src/turtlebot3/turtlebot3_cartographer/rviz/tb3_cartographer.rviz
```

4. **Run the autonomous exploration package:**

```bash
ros2 run autonomous_exploration control
```

This will start the robot's autonomous exploration.
