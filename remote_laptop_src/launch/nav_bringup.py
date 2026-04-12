#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # Get package share directory
    auto_explore_share = get_package_share_directory('auto_explore')
    
    # Declare launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) time if true'
    )
    
    enable_slam_arg = DeclareLaunchArgument(
        'enable_slam',
        default_value='true',
        description='Enable SLAM Toolbox'
    )
    
    enable_rviz_arg = DeclareLaunchArgument(
        'enable_rviz',
        default_value='true',
        description='Enable RViz visualization'
    )

    slam_params_file_arg = DeclareLaunchArgument(
        'slam_params_file',
        default_value=os.path.join(auto_explore_share, 'config', 'mapper_params_online_async.yaml'),
        description='Path to SLAM Toolbox parameter file'
    )
    
    # Launch argument substitutions
    use_sim_time = LaunchConfiguration('use_sim_time')
    enable_slam = LaunchConfiguration('enable_slam')
    enable_rviz = LaunchConfiguration('enable_rviz')
    slam_params_file = LaunchConfiguration('slam_params_file')
    
    # SLAM Toolbox node
    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            slam_params_file,
            {'use_sim_time': use_sim_time},
        ],
        condition=IfCondition(enable_slam)
    )
    
    # RViz node with turtlebot3 cartographer config
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.expanduser('~/turtlebot3_ws/src/turtlebot3/turtlebot3_cartographer/rviz/tb3_cartographer.rviz')],
        parameters=[
            {'use_sim_time': use_sim_time},
        ],
        condition=IfCondition(enable_rviz)
    )
    
    return LaunchDescription([
        use_sim_time_arg,
        enable_slam_arg,
        enable_rviz_arg,
        slam_params_file_arg,
        slam_toolbox_node,
        rviz_node,
    ])
