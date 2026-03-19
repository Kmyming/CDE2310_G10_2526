#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_context import LaunchContext
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition
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
    
    enable_markers_arg = DeclareLaunchArgument(
        'enable_markers',
        default_value='true',
        description='Enable ArUco marker detection'
    )
    
    # Launch argument substitutions
    use_sim_time = LaunchConfiguration('use_sim_time')
    enable_slam = LaunchConfiguration('enable_slam')
    enable_rviz = LaunchConfiguration('enable_rviz')
    enable_markers = LaunchConfiguration('enable_markers')
    
    # Include nav_bringup.py
    nav_bringup = IncludeLaunchDescription(
        os.path.join(auto_explore_share, 'launch', 'nav_bringup.py'),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'enable_slam': enable_slam,
            'enable_rviz': enable_rviz,
        }.items()
    )
    
    # Include global_controller_bringup.py
    controller_bringup = IncludeLaunchDescription(
        os.path.join(auto_explore_share, 'launch', 'global_controller_bringup.py'),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'enable_markers': enable_markers,
        }.items()
    )
    
    return LaunchDescription([
        use_sim_time_arg,
        enable_slam_arg,
        enable_rviz_arg,
        enable_markers_arg,
        nav_bringup,
        controller_bringup,
    ])
