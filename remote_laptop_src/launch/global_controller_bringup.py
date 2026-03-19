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
    
    enable_markers_arg = DeclareLaunchArgument(
        'enable_markers',
        default_value='true',
        description='Enable ArUco marker detection'
    )
    
    # Launch argument substitutions
    use_sim_time = LaunchConfiguration('use_sim_time')
    enable_markers = LaunchConfiguration('enable_markers')
    
    # Mission Controller (FSM) node
    mission_controller_node = Node(
        package='auto_explore',
        executable='mission_controller',
        name='mission_controller',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
        ]
    )
    
    # Exploration Controller node
    exploration_controller_node = Node(
        package='auto_explore',
        executable='exploration_controller',
        name='exploration_controller',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
        ]
    )
    
    # ArUco Pose Publisher node
    pose_publisher_node = Node(
        package='auto_explore',
        executable='pose_publisher',
        name='pose_publisher',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'image_topic': '/camera/image_raw'},
            {'camera_info_topic': '/camera/camera_info'},
            {'marker_size_m': 0.05},
            {'dictionary': 'DICT_6X6_250'},
        ],
        condition=IfCondition(enable_markers)
    )
    
    # Marker Logger (Pose Subscriber) node
    pose_subscriber_node = Node(
        package='auto_explore',
        executable='pose_subscriber',
        name='pose_subscriber',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
        ],
        condition=IfCondition(enable_markers)
    )
    
    return LaunchDescription([
        use_sim_time_arg,
        enable_markers_arg,
        mission_controller_node,
        exploration_controller_node,
        pose_publisher_node,
        pose_subscriber_node,
    ])
