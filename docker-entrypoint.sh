#!/bin/bash
set -e

# Source ROS 2 environment
if [ -f /opt/ros/humble/setup.bash ]; then
  source /opt/ros/humble/setup.bash
fi

# Source workspace if it exists
if [ -f /home/ros/ws/install/setup.bash ]; then
  source /home/ros/ws/install/setup.bash
fi

# Execute the passed command or default to bash
exec "$@"
