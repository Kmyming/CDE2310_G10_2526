#!/bin/bash
# TurtleBot3 Auto-Explore Launcher
# This script properly sets up the environment to find and launch the auto_explore package
# 
# Usage: ./launch_auto_explore.sh global_bringup.py [additional ros2 launch args...]
#

# Get the workspace directory  
WORKSPACE_DIR="/home/kmyming/turtlebot3_ws"

# Set up environment
export AMENT_PREFIX_PATH="${WORKSPACE_DIR}/install/auto_explore:${AMENT_PREFIX_PATH}"
source "${WORKSPACE_DIR}/install/setup.bash"

# Launch the specified file
ros2 launch auto_explore "$@"
