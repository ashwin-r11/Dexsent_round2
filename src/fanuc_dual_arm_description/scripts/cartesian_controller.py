#!/usr/bin/env python3
"""
Cartesian Controller Node for Dual-Arm System

Converts Cartesian pose commands to joint trajectories using simple IK.
Publishes to JointTrajectoryController for each arm.
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import Pose, PoseStamped
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import numpy as np
from scipy.spatial.transform import Rotation


class SimpleIK:
    """Simple analytical IK for 6-DOF arm (approximate)."""
    
    def __init__(self, prefix=''):
        self.prefix = prefix
        # Approximate link lengths for Fanuc CRX-10iA (meters)
        self.d1 = 0.245  # Base to joint 1
        self.a2 = 0.54   # Link 2 length
        self.a3 = 0.54   # Link 3 length
        self.d6 = 0.19   # Wrist to tool

    def solve(self, target_pose):
        """
        Compute joint angles for target pose.
        Returns list of 6 joint angles in radians.
        
        This is a simplified IK that provides approximate solutions.
        For production use, replace with KDL or MoveIt IK.
        """
        x = target_pose.position.x
        y = target_pose.position.y
        z = target_pose.position.z
        
        # Joint 1: Base rotation
        j1 = np.arctan2(y, x)
        
        # Wrist center position (approximate)
        r = np.sqrt(x**2 + y**2)
        wc_r = r - self.d6 * 0.5  # Approximate wrist center
        wc_z = z - self.d1
        
        # Joint 2 and 3: Elbow calculation
        d = np.sqrt(wc_r**2 + wc_z**2)
        d = min(d, self.a2 + self.a3 - 0.01)  # Clamp to reachable
        d = max(d, abs(self.a2 - self.a3) + 0.01)
        
        cos_j3 = (d**2 - self.a2**2 - self.a3**2) / (2 * self.a2 * self.a3)
        cos_j3 = np.clip(cos_j3, -1, 1)
        j3 = np.arccos(cos_j3)
        
        alpha = np.arctan2(wc_z, wc_r)
        beta = np.arctan2(self.a3 * np.sin(j3), self.a2 + self.a3 * np.cos(j3))
        j2 = alpha + beta
        
        # Wrist joints (simplified - point toward target orientation)
        quat = target_pose.orientation
        rot = Rotation.from_quat([quat.x, quat.y, quat.z, quat.w])
        euler = rot.as_euler('xyz')
        
        j4 = euler[2]  # Roll
        j5 = euler[1] - j2 - j3  # Pitch compensation
        j6 = euler[0]  # Yaw
        
        # Clamp to joint limits
        joints = [j1, j2, j3, j4, j5, j6]
        limits = [3.14, 2.27, 3.32, 6.28, 2.27, 6.28]
        joints = [np.clip(j, -l, l) for j, l in zip(joints, limits)]
        
        return joints


class CartesianControllerNode(Node):
    """ROS2 node for Cartesian control of dual arms."""
    
    def __init__(self):
        super().__init__('cartesian_controller')
        
        # IK solvers for each arm
        self.left_ik = SimpleIK('left_')
        self.right_ik = SimpleIK('right_')
        
        # Action clients for trajectory controllers
        self.left_action = ActionClient(
            self, FollowJointTrajectory,
            '/left_arm_controller/follow_joint_trajectory'
        )
        self.right_action = ActionClient(
            self, FollowJointTrajectory,
            '/right_arm_controller/follow_joint_trajectory'
        )
        
        # Subscribers for Cartesian commands
        self.left_sub = self.create_subscription(
            PoseStamped, '/left_arm/target_pose',
            self.left_pose_callback, 10
        )
        self.right_sub = self.create_subscription(
            PoseStamped, '/right_arm/target_pose',
            self.right_pose_callback, 10
        )
        
        # Subscriber for synchronized motion
        self.sync_sub = self.create_subscription(
            PoseStamped, '/dual_arm/sync_pose',
            self.sync_pose_callback, 10
        )
        
        # Joint names
        self.left_joints = [f'left_joint_{i}' for i in range(1, 7)]
        self.right_joints = [f'right_joint_{i}' for i in range(1, 7)]
        
        self.get_logger().info('Cartesian Controller initialized')
        self.get_logger().info('Topics: /left_arm/target_pose, /right_arm/target_pose, /dual_arm/sync_pose')

    def left_pose_callback(self, msg):
        """Handle left arm Cartesian command."""
        joints = self.left_ik.solve(msg.pose)
        self.send_trajectory(self.left_action, self.left_joints, joints, 'left_arm')

    def right_pose_callback(self, msg):
        """Handle right arm Cartesian command."""
        joints = self.right_ik.solve(msg.pose)
        self.send_trajectory(self.right_action, self.right_joints, joints, 'right_arm')

    def sync_pose_callback(self, msg):
        """Handle synchronized motion - both arms move to mirrored poses."""
        # Left arm: original pose
        left_joints = self.left_ik.solve(msg.pose)
        
        # Right arm: mirrored pose (flip Y)
        mirrored_pose = Pose()
        mirrored_pose.position.x = msg.pose.position.x
        mirrored_pose.position.y = -msg.pose.position.y  # Mirror across Y
        mirrored_pose.position.z = msg.pose.position.z
        mirrored_pose.orientation = msg.pose.orientation
        right_joints = self.right_ik.solve(mirrored_pose)
        
        # Send both simultaneously
        self.send_trajectory(self.left_action, self.left_joints, left_joints, 'left_arm')
        self.send_trajectory(self.right_action, self.right_joints, right_joints, 'right_arm')
        
        self.get_logger().info('Synchronized motion command sent')

    def send_trajectory(self, action_client, joint_names, joint_positions, arm_name):
        """Send trajectory to controller."""
        if not action_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().warn(f'{arm_name} controller not available')
            return
        
        # Create trajectory
        traj = JointTrajectory()
        traj.joint_names = joint_names
        
        point = JointTrajectoryPoint()
        point.positions = joint_positions
        point.velocities = [0.0] * 6
        point.time_from_start = Duration(sec=2, nanosec=0)
        traj.points.append(point)
        
        # Send goal
        goal = FollowJointTrajectory.Goal()
        goal.trajectory = traj
        
        future = action_client.send_goal_async(goal)
        self.get_logger().info(f'{arm_name}: Moving to Cartesian target')


def main(args=None):
    rclpy.init(args=args)
    node = CartesianControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
