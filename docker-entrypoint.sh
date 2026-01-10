#!/bin/bash
set -e

# Source ROS2 Humble
source /opt/ros/humble/setup.bash

# Build workspace if src exists and has packages
if [ -d "/ros2_ws/src" ] && [ "$(ls -A /ros2_ws/src 2>/dev/null)" ]; then
    echo "Building ROS2 workspace..."
    cd /ros2_ws
    colcon build --symlink-install 2>/dev/null || true
    
    # Source workspace if build succeeded
    if [ -f "/ros2_ws/install/setup.bash" ]; then
        source /ros2_ws/install/setup.bash
    fi
fi

echo ""
echo "========================================"
echo "  ROS2 Humble Environment Ready"
echo "========================================"
echo "  ROS_DISTRO: $ROS_DISTRO"
echo "  Workspace: /ros2_ws"
echo "========================================"
echo ""

# Execute command passed to container
exec "$@"
