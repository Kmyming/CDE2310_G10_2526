#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    auto_explore_share = get_package_share_directory('auto_explore')

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

    enable_fsm_arg = DeclareLaunchArgument(
        'enable_fsm',
        default_value='true',
        description='Enable mission FSM node'
    )

    enable_navigation_arg = DeclareLaunchArgument(
        'enable_navigation',
        default_value='true',
        description='Enable exploration/navigation controller'
    )

    enable_markers_arg = DeclareLaunchArgument(
        'enable_markers',
        default_value='true',
        description='Enable ArUco marker detection'
    )

    enable_pose_publisher_arg = DeclareLaunchArgument(
        'enable_pose_publisher',
        default_value='true',
        description='Enable pose_publisher marker node'
    )

    enable_docking_arg = DeclareLaunchArgument(
        'enable_docking',
        default_value='true',
        description='Enable docking controller'
    )

    enable_shooter_arg = DeclareLaunchArgument(
        'enable_shooter',
        default_value='true',
        description='Enable shooter controller'
    )

    shooter_enable_hardware_arg = DeclareLaunchArgument(
        'shooter_enable_hardware',
        default_value='false',
        description='Enable physical GPIO actuation for shooter'
    )

    use_sim_time = LaunchConfiguration('use_sim_time')
    enable_slam = LaunchConfiguration('enable_slam')
    enable_rviz = LaunchConfiguration('enable_rviz')
    slam_params_file = LaunchConfiguration('slam_params_file')
    enable_fsm = LaunchConfiguration('enable_fsm')
    enable_navigation = LaunchConfiguration('enable_navigation')
    enable_markers = LaunchConfiguration('enable_markers')
    enable_pose_publisher = LaunchConfiguration('enable_pose_publisher')
    enable_docking = LaunchConfiguration('enable_docking')
    enable_shooter = LaunchConfiguration('enable_shooter')
    shooter_enable_hardware = LaunchConfiguration('shooter_enable_hardware')

    nav_bringup = IncludeLaunchDescription(
        os.path.join(auto_explore_share, 'launch', 'nav_bringup.py'),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'enable_slam': enable_slam,
            'enable_rviz': enable_rviz,
            'slam_params_file': slam_params_file,
        }.items()
    )
    
    controller_bringup = IncludeLaunchDescription(
        os.path.join(auto_explore_share, 'launch', 'global_controller_bringup.py'),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'enable_fsm': enable_fsm,
            'enable_navigation': enable_navigation,
            'enable_markers': enable_markers,
            'enable_pose_publisher': enable_pose_publisher,
            'enable_docking': enable_docking,
            'enable_shooter': enable_shooter,
            'shooter_enable_hardware': shooter_enable_hardware,
        }.items()
    )

    return LaunchDescription([
        use_sim_time_arg,
        enable_slam_arg,
        enable_rviz_arg,
        slam_params_file_arg,
        enable_fsm_arg,
        enable_navigation_arg,
        enable_markers_arg,
        enable_pose_publisher_arg,
        enable_docking_arg,
        enable_shooter_arg,
        shooter_enable_hardware_arg,
        nav_bringup,
        controller_bringup,
    ])
