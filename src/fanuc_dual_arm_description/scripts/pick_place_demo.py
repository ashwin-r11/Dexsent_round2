#!/usr/bin/env python3
"""
Pick and Place Demo for Dual-Arm System

Demonstrates coordinated pick-and-place of a workpiece using both arms and grippers.
Arms work together to pick up, move, and place the workpiece.
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory, GripperCommand
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import time


class PickPlaceDemo(Node):
    """Demo node for pick-and-place with dual arms."""
    
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
        
        self.get_logger().info('Pick & Place Demo initialized')
        self.get_logger().info('Waiting for arm controllers...')
        
        # Wait for arm controllers
        self.left_arm.wait_for_server()
        self.right_arm.wait_for_server()
        self.get_logger().info('Arm controllers ready!')
        
        # Demo sequence
        self.demo_step = 0
        self.create_timer(3.5, self.run_demo)

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
        # Note: Gripper controller may not be active - this is for demonstration
        position = 0.04 if open_grippers else 0.0  # Open = 0.04, Closed = 0.0
        self.get_logger().info(f'Grippers: {"OPEN" if open_grippers else "CLOSE"}')
        
        # If gripper controllers are available, send commands
        # For now, just log the action
        return

    def run_demo(self):
        """Execute pick-and-place sequence."""
        
        # Define movements as deltas from neutral
        # Avoid collision by keeping arms separated
        sequence = [
            # Step 0: Start position - arms neutral
            ("HOME position", 
             [0, 0, 0, 0, 0, 0], 
             [0, 0, 0, 0, 0, 0], 
             True),  # grippers open
            
            # Step 1: Move to pre-grasp (above workpiece)
            ("APPROACH workpiece", 
             [0.2, -0.2, 0.3, 0, 0, 0],   # left reaches toward center
             [-0.2, 0.2, -0.3, 0, 0, 0],  # right reaches toward center (mirror)
             True),
            
            # Step 2: Lower to grasp position
            ("GRASP position", 
             [0.2, 0, 0.5, 0, 0, 0],      # left lowers
             [-0.2, 0, -0.5, 0, 0, 0],    # right lowers (mirror)
             True),
            
            # Step 3: Close grippers
            ("GRIP workpiece", 
             [0.2, 0, 0.5, 0, 0, 0],      # same position
             [-0.2, 0, -0.5, 0, 0, 0],    # same position
             False),  # grippers close
            
            # Step 4: Lift workpiece
            ("LIFT workpiece", 
             [0.2, -0.3, 0.3, 0, 0, 0],   # lift up
             [-0.2, 0.3, -0.3, 0, 0, 0],  # lift up (mirror)
             False),
            
            # Step 5: Move to new position (shift sideways)
            ("MOVE to target", 
             [0.4, -0.3, 0.3, 0, 0, 0],   # move left
             [-0.4, 0.3, -0.3, 0, 0, 0],  # move right (mirror)
             False),
            
            # Step 6: Lower to place
            ("PLACE position", 
             [0.4, 0, 0.5, 0, 0, 0],      # lower
             [-0.4, 0, -0.5, 0, 0, 0],    # lower (mirror)
             False),
            
            # Step 7: Open grippers - release
            ("RELEASE workpiece", 
             [0.4, 0, 0.5, 0, 0, 0],      # same position
             [-0.4, 0, -0.5, 0, 0, 0],    # same position
             True),  # grippers open
            
            # Step 8: Retreat
            ("RETREAT", 
             [0.2, -0.3, 0.3, 0, 0, 0],   # back up
             [-0.2, 0.3, -0.3, 0, 0, 0],  # back up (mirror)
             True),
            
            # Step 9: Return home
            ("Return HOME", 
             [0, 0, 0, 0, 0, 0], 
             [0, 0, 0, 0, 0, 0], 
             True),
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
            self.get_logger().info('=== PICK & PLACE COMPLETE! Restarting... ===')
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
