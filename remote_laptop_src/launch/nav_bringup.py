#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
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

    slam_start_delay_arg = DeclareLaunchArgument(
        'slam_start_delay_sec',
        default_value='10.0',
        description='Delay before starting SLAM Toolbox to let TF and scan publishers stabilize (6s for real robot, 2s for sim)'
    )

    rviz_start_delay_arg = DeclareLaunchArgument(
        'rviz_start_delay_sec',
        default_value='10.0',
        description='Delay before starting RViz so SLAM/TF are available first'
    )
    
    # Launch argument substitutions
    use_sim_time = LaunchConfiguration('use_sim_time')
    enable_slam = LaunchConfiguration('enable_slam')
    enable_rviz = LaunchConfiguration('enable_rviz')
    slam_params_file = LaunchConfiguration('slam_params_file')
    slam_start_delay_sec = LaunchConfiguration('slam_start_delay_sec')
    rviz_start_delay_sec = LaunchConfiguration('rviz_start_delay_sec')
    
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

    delayed_slam_toolbox_node = TimerAction(
        period=slam_start_delay_sec,
        actions=[slam_toolbox_node],
        condition=IfCondition(enable_slam)
    )
    
    # RViz node with turtlebot3 cartographer config
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        prefix='env XDG_DATA_DIRS=/usr/local/share:/usr/share LD_LIBRARY_PATH=/opt/ros/humble/opt/rviz_ogre_vendor/lib:/opt/ros/humble/lib/x86_64-linux-gnu:/opt/ros/humble/lib:/usr/lib/x86_64-linux-gnu GTK_MODULES= GTK_PATH= GIO_EXTRA_MODULES=',
        arguments=['-d', os.path.expanduser('~/turtlebot3_ws/src/turtlebot3/turtlebot3_cartographer/rviz/tb3_cartographer.rviz')],
        parameters=[
            {'use_sim_time': use_sim_time},
        ],
        condition=IfCondition(enable_rviz)
    )

    delayed_rviz_node = TimerAction(
        period=rviz_start_delay_sec,
        actions=[rviz_node],
        condition=IfCondition(enable_rviz)
    )
    
    return LaunchDescription([
        use_sim_time_arg,
        enable_slam_arg,
        enable_rviz_arg,
        slam_params_file_arg,
        slam_start_delay_arg,
        rviz_start_delay_arg,
        delayed_slam_toolbox_node,
        delayed_rviz_node,
    ])
