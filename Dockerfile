# Dockerfile - Ubuntu 22.04 with ROS2 Humble + MoveIt + ros2_control
FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV ROS_DISTRO=humble

# install basic tools and add ROS2 apt repository
# ---- Base system tools (NO ROS packages here) ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg2 lsb-release ca-certificates sudo \
    git wget build-essential \
    python3-pip \
    locales tzdata software-properties-common \
    && locale-gen en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*


# Add ROS 2 apt repository (recommended key method)
RUN mkdir -p /usr/share/keyrings \
    && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | gpg --dearmour -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" \
    > /etc/apt/sources.list.d/ros2.list

# Install ROS2 Humble desktop and MoveIt + ros2_control packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-${ROS_DISTRO}-desktop \
    ros-${ROS_DISTRO}-moveit \
    ros-${ROS_DISTRO}-ros2-control \
    ros-${ROS_DISTRO}-ros2-controllers \
    ros-${ROS_DISTRO}-joint-state-publisher-gui \
    ros-${ROS_DISTRO}-xacro \
    ros-${ROS_DISTRO}-robot-state-publisher \
    python3-rosdep \
    python3-colcon-common-extensions \
    python3-vcstool \
    && rm -rf /var/lib/apt/lists/*

# Initialize rosdep (so building workspaces works)
RUN rosdep init || true
RUN rosdep update || true

# Create a non-root user 'ros' matching common host UID (1000)
ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd -m -u ${USER_UID} -g ${USER_GID} -s /bin/bash ${USERNAME} \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Workspace placeholder (optional)
USER ${USERNAME}
WORKDIR /home/${USERNAME}

# Small helper entrypoint that sources ROS setup
USER root
COPY docker-entrypoint.sh /ros_entrypoint.sh
RUN chmod +x /ros_entrypoint.sh
USER ${USERNAME}
ENV HOME=/home/${USERNAME}
RUN echo "source /opt/ros/humble/setup.bash" >> /home/${USERNAME}/.bashrc \
    && echo "if [ -f /home/ros/ws/install/setup.bash ]; then source /home/ros/ws/install/setup.bash; fi" >> /home/${USERNAME}/.bashrc
ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]
