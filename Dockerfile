# ROS2 Humble on Ubuntu 22.04
FROM osrf/ros:humble-desktop-full

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install essential packages
RUN apt-get update && apt-get install -y \
    # Build tools
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    # MoveIt2 and ros2_control
    ros-humble-moveit \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-gripper-controllers \
    ros-humble-joint-state-publisher-gui \
    ros-humble-xacro \
    ros-humble-robot-state-publisher \
    ros-humble-rviz2 \
    # Gazebo (optional, for simulation)
    ros-humble-gazebo-ros2-control \
    ros-humble-gazebo-ros-pkgs \
    # Utilities
    git \
    wget \
    curl \
    vim \
    nano \
    terminator \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /ros2_ws

# Copy entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["bash"]
