#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition
import os


def generate_launch_description():
    auto_explore_share = get_package_share_directory('auto_explore')

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) time if true'
    )

    nav_params_file_arg = DeclareLaunchArgument(
        'nav_params_file',
        default_value=os.path.join(auto_explore_share, 'config', 'params.yaml'),
        description='Path to navigation parameters YAML file'
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
        description='Enable physical GPIO actuation for shooter (keep false in Gazebo)'
    )

    use_sim_time = LaunchConfiguration('use_sim_time')
    nav_params_file = LaunchConfiguration('nav_params_file')
    enable_fsm = LaunchConfiguration('enable_fsm')
    enable_navigation = LaunchConfiguration('enable_navigation')
    enable_markers = LaunchConfiguration('enable_markers')
    enable_docking = LaunchConfiguration('enable_docking')
    enable_shooter = LaunchConfiguration('enable_shooter')
    shooter_enable_hardware = LaunchConfiguration('shooter_enable_hardware')

    mission_controller_node = Node(
        package='auto_explore',
        executable='mission_controller',
        name='mission_controller',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
        ],
        condition=IfCondition(enable_fsm)
    )

    exploration_controller_node = Node(
        package='auto_explore',
        executable='exploration_controller',
        name='exploration_controller',
        output='screen',
        parameters=[
            nav_params_file,
            {'use_sim_time': use_sim_time},
        ],
        condition=IfCondition(enable_navigation)
    )

    pose_publisher_node = Node(
        package='auto_explore',
        executable='pose_publisher',
        name='pose_publisher',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'image_topic': '/camera/image_raw'},
            {'camera_info_topic': '/camera/camera_info'},
            {'marker_size_m': 0.053},
            {'dictionary': 'DICT_4X4_250'},
        ],
        condition=IfCondition(enable_markers)
    )

    docking_controller_node = Node(
        package='auto_explore',
        executable='docking_controller',
        name='docking_controller',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'dock_cycle_timeout_sec': 20.0},
            {'target_marker_id': -1},
        ],
        condition=IfCondition(enable_docking)
    )

    shooter_controller_node = Node(
        package='auto_explore',
        executable='shooter_controller',
        name='shooter_controller',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'enable_hardware': shooter_enable_hardware},
        ],
        condition=IfCondition(enable_shooter)
    )

    return LaunchDescription([
        use_sim_time_arg,
        nav_params_file_arg,
        enable_fsm_arg,
        enable_navigation_arg,
        enable_markers_arg,
        enable_docking_arg,
        enable_shooter_arg,
        shooter_enable_hardware_arg,
        mission_controller_node,
        exploration_controller_node,
        pose_publisher_node,
        docking_controller_node,
        shooter_controller_node,
    ])
