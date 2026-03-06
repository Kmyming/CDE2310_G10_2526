# TurtleBot3 Simple Maze World

This world file creates a simple maze environment for basic navigation, SLAM, and autonomous driving testing with the TurtleBot3 platform.

## Overview

The simple maze world provides a clean testing environment for:

### Key Features

1. **🟢 Start Zone**: Green platform at (-5, -3) where the robot begins
2. **🧱 Maze Layout**: Multiple internal walls creating navigation challenges
3. **🏗️ Outer Boundaries**: Perimeter walls defining the maze area
4. **💡 Proper Lighting**: Multiple light sources for realistic conditions

### World Layout

```
    +---+---+---+---+---+---+---+---+---+---+---+---+
    |       |                           |           |
    |       |                           |     |     |
    |       |                           |     |     |
    |   +---+                           +-----+     |
    |       |                                       |
    |   +---+---+   +---+                          |
    |           |   |                               |
    |   |       |   |       +---+                  |
    |   |       |           |                      |
    | [S]       |           |           +---+      |
    |           |           |                      |
    +---+---+---+---+---+---+---+---+---+---+---+---+

Legend:
[S] = Start Zone (Green Platform)
+---+ = Walls and obstacles
```

## Usage Instructions

### 1. Launch the Simple Maze World

```bash
# Set TurtleBot3 model
export TURTLEBOT3_MODEL=burger

# Launch the simple maze simulation
ros2 launch turtlebot3_gazebo simple_maze.launch.py
```

### 2. Manual Control (Testing)

```bash
# Launch teleop for manual control during testing
ros2 run turtlebot3_teleop teleop_keyboard
```

### 3. SLAM Navigation

```bash
# Launch SLAM for mapping
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True

# Launch navigation stack
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True
```

## Navigation Features

### **Perfect for Learning**
- **Clean Environment**: No distracting elements, just pure navigation
- **Multiple Paths**: Various routes through the maze for path planning
- **Dead Ends**: Challenges for obstacle avoidance algorithms
- **Open Areas**: Spaces for turning and maneuvering

### **SLAM Testing**
- **Wall Detection**: Clear walls for LiDAR-based SLAM
- **Loop Closure**: Opportunities for map loop closure detection
- **Feature Rich**: Multiple corners and openings for localization
- **Bounded Area**: Defined boundaries for complete mapping

### **Algorithm Development**
- **Path Planning**: Test A*, RRT, or other planning algorithms  
- **Obstacle Avoidance**: Dynamic and static obstacle handling
- **Localization**: Test AMCL and other localization methods
- **Exploration**: Autonomous exploration algorithms

## ROS Topics

The maze world publishes standard TurtleBot3 topics:

- `/scan` - LiDAR data for navigation and mapping
- `/odom` - Odometry for localization  
- `/cmd_vel` - Velocity commands for movement
- `/joint_states` - Robot joint information
- `/imu` - Inertial measurement data
- `/tf` - Transform tree for coordinate frames

## World Specifications

### **Dimensions**
- **Total Area**: 12m x 8m
- **Wall Height**: 1.5m for interior walls, 2m for outer walls
- **Wall Thickness**: 0.2m for reliable collision detection
- **Floor**: Flat gray surface with proper friction

### **Lighting**
- **Directional Light**: Main overhead lighting
- **Point Lights**: Two additional lights for even illumination
- **Shadows**: Enabled for realistic visual feedback

### **Physics**
- **Simulation**: ODE physics engine
- **Step Size**: 0.001s for accurate simulation
- **Real-time Factor**: 1.0 for real-time performance
- **Collision**: Proper collision detection for all walls

## Customization

### Adding More Walls
Edit `simple_maze.world` to add additional maze walls:

```xml
<model name="maze_wall_9">
  <static>true</static>
  <link name="link">
    <visual name="visual">
      <geometry>
        <box>
          <size>length width height</size>
        </box>
      </geometry>
    </visual>
    <collision name="collision">
      <geometry>
        <box>
          <size>length width height</size>
        </box>
      </geometry>
    </collision>
  </link>
  <pose>x y z 0 0 0</pose>
</model>
```

### Modifying Start Position
Change the robot spawn position by editing the launch file:
```python
x_pose = LaunchConfiguration('x_pose', default='your_x')
y_pose = LaunchConfiguration('y_pose', default='your_y')
```

### Adding Landmarks
Place markers for navigation testing:
- QR codes on walls for localization
- ArUco markers for visual navigation
- Colored objects for detection testing

## Performance Tips

### **Simulation Performance**
- Reduce physics step size if simulation is too fast
- Increase step size if simulation is too slow
- Adjust lighting for better visual performance

### **Navigation Tuning**
- Adjust LiDAR parameters for better wall detection
- Tune SLAM parameters for the maze size
- Configure navigation stack for maze-specific challenges

## Troubleshooting

### Common Issues

1. **Robot doesn't spawn**: Check TURTLEBOT3_MODEL environment variable
2. **Walls not detected**: Verify LiDAR range and angle settings  
3. **Poor performance**: Reduce physics step size or complexity
4. **Navigation issues**: Check coordinate frames and transforms

### **Maze Too Easy/Hard?**
- **Too Easy**: Add more walls and complexity
- **Too Hard**: Remove some walls or widen passages
- **Just Right**: Perfect for learning and testing!

## Files Structure

```
turtlebot3_gazebo/
├── worlds/
│   └── simple_maze.world          # Main maze world file  
├── launch/
│   └── simple_maze.launch.py      # Launch simple maze simulation
└── README_maze.md                 # This documentation
```

This simple maze world provides the perfect foundation for learning autonomous navigation, developing SLAM algorithms, and testing path planning without the complexity of delivery missions or multi-level environments! 🤖🗺️