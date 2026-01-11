#!/usr/bin/env python3
"""
Synchronized Motion Demo for Dual-Arm System

Demonstrates SYMMETRIC coordinated movement of both arms using direct joint commands.
Uses the actual neutral pose values configured in the URDF.
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class SyncMotionDemo(Node):
    """Demo node for synchronized symmetric dual-arm motion."""
    
    # Neutral pose from URDF (screenshot values)
    NEUTRAL_LEFT = [-0.017, 1.614, 0.0, -3.209, 0.0, 0.0]
    NEUTRAL_RIGHT = [-3.142, -1.580, -3.031, -3.029, 0.085, 0.0]
    
    def __init__(self):
        super().__init__('sync_motion_demo')
        
        # Action clients for trajectory controllers
        self.left_action = ActionClient(
            self, FollowJointTrajectory,
            '/left_arm_controller/follow_joint_trajectory'
        )
        self.right_action = ActionClient(
            self, FollowJointTrajectory,
            '/right_arm_controller/follow_joint_trajectory'
        )
        
        # Joint names
        self.left_joints = [f'left_joint_{i}' for i in range(1, 7)]
        self.right_joints = [f'right_joint_{i}' for i in range(1, 7)]
        
        self.get_logger().info('Sync Motion Demo initialized')
        self.get_logger().info('Waiting for controllers...')
        
        # Wait for controllers
        self.left_action.wait_for_server()
        self.right_action.wait_for_server()
        self.get_logger().info('Controllers ready!')
        
        # Demo sequence
        self.demo_step = 0
        self.create_timer(3.0, self.run_demo)

    def add_delta(self, base_joints, deltas):
        """Add deltas to base joint values."""
        return [b + d for b, d in zip(base_joints, deltas)]

    def send_motion(self, left_joints, right_joints, duration_sec=2.0):
        """Send trajectories to both arms."""
        # Left arm trajectory
        left_traj = JointTrajectory()
        left_traj.joint_names = self.left_joints
        left_point = JointTrajectoryPoint()
        left_point.positions = left_joints
        left_point.velocities = [0.0] * 6
        left_point.time_from_start = Duration(sec=int(duration_sec), nanosec=0)
        left_traj.points.append(left_point)
        
        # Right arm trajectory
        right_traj = JointTrajectory()
        right_traj.joint_names = self.right_joints
        right_point = JointTrajectoryPoint()
        right_point.positions = right_joints
        right_point.velocities = [0.0] * 6
        right_point.time_from_start = Duration(sec=int(duration_sec), nanosec=0)
        right_traj.points.append(right_point)
        
        # Send both goals simultaneously
        left_goal = FollowJointTrajectory.Goal()
        left_goal.trajectory = left_traj
        right_goal = FollowJointTrajectory.Goal()
        right_goal.trajectory = right_traj
        
        self.left_action.send_goal_async(left_goal)
        self.right_action.send_goal_async(right_goal)

    def run_demo(self):
        """Execute symmetric demo sequence using delta movements from neutral."""
        
        # Symmetric deltas: [j1, j2, j3, j4, j5, j6]
        # For mirror effect: left and right get same deltas (already symmetric in neutral)
        poses = [
            # Step 0: Return to neutral
            ("NEUTRAL position", [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]),
            
            # Step 1: Both arms raise up (j2 negative = up)
            ("Arms UP", [0, -0.4, 0, 0, 0, 0], [0, 0.4, 0, 0, 0, 0]),
            
            # Step 2: Both arms spread outward (j1 rotation)
            ("Arms SPREAD", [0.3, 0, 0, 0, 0, 0], [-0.3, 0, 0, 0, 0, 0]),
            
            # Step 3: Both arms inward (j1 rotation opposite)
            ("Arms INWARD", [-0.3, 0, 0, 0, 0, 0], [0.3, 0, 0, 0, 0, 0]),
            
            # Step 4: Arms forward (j3 extension)
            ("Arms FORWARD", [0, 0, 0.5, 0, 0, 0], [0, 0, -0.5, 0, 0, 0]),
            
            # Step 5: Back to neutral
            ("Back to NEUTRAL", [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]),
        ]
        
        if self.demo_step < len(poses):
            name, left_delta, right_delta = poses[self.demo_step]
            left_joints = self.add_delta(self.NEUTRAL_LEFT, left_delta)
            right_joints = self.add_delta(self.NEUTRAL_RIGHT, right_delta)
            
            self.get_logger().info(f'Step {self.demo_step + 1}: {name}')
            self.send_motion(left_joints, right_joints)
            self.demo_step += 1
        else:
            self.get_logger().info('Demo complete! Repeating...')
            self.demo_step = 0


def main(args=None):
    rclpy.init(args=args)
    node = SyncMotionDemo()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
