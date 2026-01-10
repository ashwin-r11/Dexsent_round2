import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro


def generate_launch_description():
    pkg_dir = get_package_share_directory('fanuc_dual_arm_description')
    xacro_file = os.path.join(pkg_dir, 'urdf', 'dual_arm.urdf.xacro')
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
        # Joint State Publisher GUI for testing
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
        ),
        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
        ),
    ])
