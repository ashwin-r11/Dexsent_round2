#!/usr/bin/env python3
"""
Pick and Place Demo for Dual-Arm System

Demonstrates coordinated pick-and-place with gripper control.
Arms stay well separated to avoid any collision.
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory, GripperCommand
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class PickPlaceDemo(Node):
    """Demo node for safe pick-and-place with dual arms and grippers."""
    
    # Neutral pose from URDF
    NEUTRAL_LEFT = [-0.017, 1.614, 0.0, -3.209, 0.0, 0.0]
    NEUTRAL_RIGHT = [-3.142, -1.580, -3.031, -3.029, 0.085, 0.0]
    
    def __init__(self):
        super().__init__('pick_place_demo')
        
        # Arm trajectory action clients
        self.left_arm = ActionClient(
            self, FollowJointTrajectory,
            '/left_arm_controller/follow_joint_trajectory'
        )
        self.right_arm = ActionClient(
            self, FollowJointTrajectory,
            '/right_arm_controller/follow_joint_trajectory'
        )
        
        # Gripper action clients
        self.left_gripper = ActionClient(
            self, GripperCommand,
            '/left_gripper_controller/gripper_cmd'
        )
        self.right_gripper = ActionClient(
            self, GripperCommand,
            '/right_gripper_controller/gripper_cmd'
        )
        
        # Joint names
        self.left_joints = [f'left_joint_{i}' for i in range(1, 7)]
        self.right_joints = [f'right_joint_{i}' for i in range(1, 7)]
        
        self.get_logger().info('Pick & Place Demo with Grippers')
        self.get_logger().info('Waiting for controllers...')
        
        self.left_arm.wait_for_server()
        self.right_arm.wait_for_server()
        self.get_logger().info('Arm controllers ready!')
        
        # Wait for gripper controllers
        gripper_ready = self.left_gripper.wait_for_server(timeout_sec=2.0)
        gripper_ready = gripper_ready and self.right_gripper.wait_for_server(timeout_sec=2.0)
        if gripper_ready:
            self.get_logger().info('Gripper controllers ready!')
        else:
            self.get_logger().warn('Gripper controllers not available - will skip gripper actions')
        
        self.grippers_available = gripper_ready
        self.demo_step = 0
        self.create_timer(3.0, self.run_demo)

    def add_delta(self, base, deltas):
        """Add deltas to base joint values."""
        return [b + d for b, d in zip(base, deltas)]

    def move_arms(self, left_joints, right_joints, duration=2.0):
        """Send trajectories to both arms."""
        # Left arm
        left_traj = JointTrajectory()
        left_traj.joint_names = self.left_joints
        pt = JointTrajectoryPoint()
        pt.positions = left_joints
        pt.velocities = [0.0] * 6
        pt.time_from_start = Duration(sec=int(duration), nanosec=0)
        left_traj.points.append(pt)
        
        left_goal = FollowJointTrajectory.Goal()
        left_goal.trajectory = left_traj
        self.left_arm.send_goal_async(left_goal)
        
        # Right arm
        right_traj = JointTrajectory()
        right_traj.joint_names = self.right_joints
        pt2 = JointTrajectoryPoint()
        pt2.positions = right_joints
        pt2.velocities = [0.0] * 6
        pt2.time_from_start = Duration(sec=int(duration), nanosec=0)
        right_traj.points.append(pt2)
        
        right_goal = FollowJointTrajectory.Goal()
        right_goal.trajectory = right_traj
        self.right_arm.send_goal_async(right_goal)

    def control_grippers(self, open_grippers=True):
        """Open or close both grippers."""
        if not self.grippers_available:
            self.get_logger().info(f'Grippers (simulated): {"OPEN" if open_grippers else "CLOSE"}')
            return
            
        # position: 0.04 = fully open, 0.0 = closed
        position = 0.04 if open_grippers else 0.0
        
        # Left gripper
        left_goal = GripperCommand.Goal()
        left_goal.command.position = position
        left_goal.command.max_effort = 10.0
        self.left_gripper.send_goal_async(left_goal)
        
        # Right gripper
        right_goal = GripperCommand.Goal()
        right_goal.command.position = position
        right_goal.command.max_effort = 10.0
        self.right_gripper.send_goal_async(right_goal)
        
        self.get_logger().info(f'Grippers: {"OPEN" if open_grippers else "CLOSE"}')

    def run_demo(self):
        """Execute SAFE pick-and-place with gripper control."""
        
        # SAFE movements + gripper control
        sequence = [
            # (name, left_delta, right_delta, gripper_open)
            ("HOME + OPEN grippers", [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], True),
            ("Arms UP", [0, -0.3, 0, 0, 0, 0], [0, 0.3, 0, 0, 0, 0], True),
            ("Arms FORWARD", [0, -0.2, 0.3, 0, 0, 0], [0, 0.2, -0.3, 0, 0, 0], True),
            ("CLOSE grippers (GRIP)", [0, -0.2, 0.3, 0, 0, 0], [0, 0.2, -0.3, 0, 0, 0], False),
            ("LIFT", [0, -0.5, 0.2, 0, 0, 0], [0, 0.5, -0.2, 0, 0, 0], False),
            ("MOVE to side", [0.15, -0.5, 0.2, 0, 0, 0], [-0.15, 0.5, -0.2, 0, 0, 0], False),
            ("LOWER", [0.15, -0.2, 0.3, 0, 0, 0], [-0.15, 0.2, -0.3, 0, 0, 0], False),
            ("OPEN grippers (RELEASE)", [0.15, -0.2, 0.3, 0, 0, 0], [-0.15, 0.2, -0.3, 0, 0, 0], True),
            ("RETRACT", [0, -0.4, 0, 0, 0, 0], [0, 0.4, 0, 0, 0, 0], True),
            ("HOME", [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], True),
        ]
        
        if self.demo_step < len(sequence):
            name, left_delta, right_delta, gripper_open = sequence[self.demo_step]
            left = self.add_delta(self.NEUTRAL_LEFT, left_delta)
            right = self.add_delta(self.NEUTRAL_RIGHT, right_delta)
            
            self.get_logger().info(f'Step {self.demo_step + 1}/{len(sequence)}: {name}')
            self.control_grippers(gripper_open)
            self.move_arms(left, right)
            self.demo_step += 1
        else:
            self.get_logger().info('=== DEMO COMPLETE! Restarting... ===')
            self.demo_step = 0


def main(args=None):
    rclpy.init(args=args)
    node = PickPlaceDemo()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
