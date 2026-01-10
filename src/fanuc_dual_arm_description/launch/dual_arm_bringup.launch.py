import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro


def generate_launch_description():
    pkg_dir = get_package_share_directory('fanuc_dual_arm_description')
    xacro_file = os.path.join(pkg_dir, 'urdf', 'dual_arm.urdf.xacro')
    controllers_file = os.path.join(pkg_dir, 'config', 'dual_arm_controllers.yaml')
    rviz_config = os.path.join(pkg_dir, 'rviz', 'dual_arm.rviz')

    # Process xacro
    robot_description = xacro.process_file(xacro_file).toxml()

    return LaunchDescription([
        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
        ),
        # ros2_control Controller Manager
        Node(
            package='controller_manager',
            executable='ros2_control_node',
            parameters=[
                {'robot_description': robot_description},
                controllers_file,
            ],
            output='screen',
        ),
        # Spawn Joint State Broadcaster
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        ),
        # Spawn Left Arm Controller
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['left_arm_controller', '--controller-manager', '/controller_manager'],
        ),
        # Spawn Right Arm Controller
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['right_arm_controller', '--controller-manager', '/controller_manager'],
        ),
        # Spawn Left Gripper Controller
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['left_gripper_controller', '--controller-manager', '/controller_manager'],
        ),
        # Spawn Right Gripper Controller
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['right_gripper_controller', '--controller-manager', '/controller_manager'],
        ),
        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
        ),
    ])
