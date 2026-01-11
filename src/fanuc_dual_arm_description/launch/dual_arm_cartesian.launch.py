#!/usr/bin/env python3
"""
Launch file for Dual-Arm Cartesian Control

Launches:
- Robot state publisher with dual-arm URDF
- ros2_control with JointTrajectoryControllers
- Cartesian controller node for IK
- RViz for visualization
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
import os
import xacro


def generate_launch_description():
    pkg_path = get_package_share_directory('fanuc_dual_arm_description')
    
    # Process URDF
    xacro_file = os.path.join(pkg_path, 'urdf', 'dual_arm.urdf.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()
    
    # Controller config
    controller_config = os.path.join(pkg_path, 'config', 'dual_arm_controllers.yaml')
    
    # RViz config
    rviz_config = os.path.join(pkg_path, 'rviz', 'dual_arm.rviz')
    
    return LaunchDescription([
        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen'
        ),
        
        # ros2_control_node
        Node(
            package='controller_manager',
            executable='ros2_control_node',
            parameters=[
                {'robot_description': robot_description},
                controller_config
            ],
            output='screen'
        ),
        
        # Spawn controllers
        ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'joint_state_broadcaster'],
            output='screen'
        ),
        ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'left_arm_controller'],
            output='screen'
        ),
        ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'right_arm_controller'],
            output='screen'
        ),
        ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'left_gripper_controller'],
            output='screen'
        ),
        ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'right_gripper_controller'],
            output='screen'
        ),
        
        # Cartesian Controller Node
        Node(
            package='fanuc_dual_arm_description',
            executable='cartesian_controller.py',
            name='cartesian_controller',
            output='screen'
        ),
        
        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
            output='screen'
        ),
    ])
