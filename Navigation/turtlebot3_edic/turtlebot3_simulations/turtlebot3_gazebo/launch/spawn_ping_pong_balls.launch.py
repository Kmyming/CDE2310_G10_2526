#!/usr/bin/env python3
#
# Spawn Ping Pong Balls Launch File
# This launch file spawns 3 ping pong balls for the warehouse delivery mission
#

import os
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # Define spawn positions for the 3 ping pong balls
    # Place them near the start zone for easy pickup
    ball_positions = [
        {'name': 'ping_pong_ball_1', 'x': '-4.5', 'y': '-2.5', 'z': '0.5'},
        {'name': 'ping_pong_ball_2', 'x': '-4.3', 'y': '-2.7', 'z': '0.5'},
        {'name': 'ping_pong_ball_3', 'x': '-4.7', 'y': '-2.7', 'z': '0.5'},
    ]
    
    spawn_commands = []
    
    for i, pos in enumerate(ball_positions):
        spawn_ball = Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-name', pos['name'],
                '-file', '/home/jw/turtlebot3_ws/src/turtlebot3_edic/turtlebot3_simulations/turtlebot3_gazebo/models/ping_pong_ball/model.sdf',
                '-x', pos['x'],
                '-y', pos['y'],
                '-z', pos['z']
            ],
            output='screen',
        )
        spawn_commands.append(spawn_ball)

    ld = LaunchDescription()
    
    # Add all spawn commands
    for cmd in spawn_commands:
        ld.add_action(cmd)
    
    return ld