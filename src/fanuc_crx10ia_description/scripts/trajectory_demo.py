#!/usr/bin/env python3
"""
Task 1 Trajectory Demo - Demonstrates FollowJointTrajectory with single arm + gripper.

Usage:
    1. Launch bringup: ros2 launch fanuc_crx10ia_description bringup.launch.py
    2. Run this demo:  python3 scripts/trajectory_demo.py
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory, GripperCommand
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import time


class TrajectoryDemo(Node):
    def __init__(self):
        super().__init__('trajectory_demo')
        
        # Action clients
        self.arm_client = ActionClient(
            self, FollowJointTrajectory,
            '/arm_controller/follow_joint_trajectory'
        )
        self.gripper_client = ActionClient(
            self, GripperCommand,
            '/gripper_controller/gripper_cmd'
        )
        
        # Arm joint names
        self.arm_joints = [
            'joint_1', 'joint_2', 'joint_3',
            'joint_4', 'joint_5', 'joint_6'
        ]
        
        self.get_logger().info('Waiting for action servers...')
        self.arm_client.wait_for_server()
        self.gripper_client.wait_for_server()
        self.get_logger().info('Action servers ready!')

    def move_arm(self, positions, duration_sec=3.0):
        """Send arm to specified joint positions."""
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = self.arm_joints
        
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=int(duration_sec), nanosec=0)
        goal.trajectory.points = [point]
        
        self.get_logger().info(f'Moving arm to: {positions}')
        future = self.arm_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Arm goal rejected!')
            return False
        
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        self.get_logger().info('Arm motion complete.')
        return True

    def move_gripper(self, position, max_effort=10.0):
        """Open/close gripper. position=0.0 (closed), 0.04 (open)."""
        goal = GripperCommand.Goal()
        goal.command.position = position
        goal.command.max_effort = max_effort
        
        action = 'Opening' if position > 0.02 else 'Closing'
        self.get_logger().info(f'{action} gripper...')
        
        future = self.gripper_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Gripper goal rejected!')
            return False
        
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        self.get_logger().info('Gripper motion complete.')
        return True

    def run_demo(self):
        """Execute demo sequence."""
        self.get_logger().info('=== Starting Trajectory Demo ===')
        
        # Home position
        home = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        # Demo poses (radians)
        pose1 = [0.5, -0.3, 0.4, 0.0, 0.5, 0.0]   # Reach forward
        pose2 = [-0.5, -0.3, 0.4, 0.0, 0.5, 0.0]  # Reach to side
        pose3 = [0.0, -0.5, 0.6, 0.0, 0.8, 0.0]   # Reach down
        
        # Demo sequence
        self.get_logger().info('Step 1: Go to home position')
        self.move_arm(home, 2.0)
        time.sleep(0.5)
        
        self.get_logger().info('Step 2: Open gripper')
        self.move_gripper(0.04)  # Open
        time.sleep(0.5)
        
        self.get_logger().info('Step 3: Move to pose 1')
        self.move_arm(pose1, 3.0)
        time.sleep(0.5)
        
        self.get_logger().info('Step 4: Close gripper (simulate grasp)')
        self.move_gripper(0.0)  # Close
        time.sleep(0.5)
        
        self.get_logger().info('Step 5: Move to pose 2')
        self.move_arm(pose2, 3.0)
        time.sleep(0.5)
        
        self.get_logger().info('Step 6: Move to pose 3')
        self.move_arm(pose3, 3.0)
        time.sleep(0.5)
        
        self.get_logger().info('Step 7: Open gripper (release)')
        self.move_gripper(0.04)  # Open
        time.sleep(0.5)
        
        self.get_logger().info('Step 8: Return to home')
        self.move_arm(home, 3.0)
        
        self.get_logger().info('=== Demo Complete ===')


def main():
    rclpy.init()
    demo = TrajectoryDemo()
    
    try:
        demo.run_demo()
    except KeyboardInterrupt:
        pass
    finally:
        demo.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
