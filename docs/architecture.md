# System Architecture

Technical architecture overview of the dual-arm ROS2 system.

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                           (RViz2)                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ROS2 MIDDLEWARE                            │
│                         (DDS)                                   │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ robot_state_    │  │ controller_     │  │ cartesian_      │
│ publisher       │  │ manager         │  │ controller      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ros2_control                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ joint_state │  │ left_arm    │  │ right_arm   │             │
│  │ _broadcaster│  │ _controller │  │ _controller │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│  ┌─────────────┐  ┌─────────────┐                              │
│  │ left_grip   │  │ right_grip  │                              │
│  │ _controller │  │ _controller │                              │
│  └─────────────┘  └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HARDWARE INTERFACE                           │
│              (fake_components/GenericSystem)                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Package Dependency Graph

```
fanuc_dual_arm_description
         │
         ├── fanuc_crx10ia_description (mesh files)
         │
         ├── ros2_control
         │
         ├── ros2_controllers
         │     ├── joint_trajectory_controller
         │     ├── joint_state_broadcaster
         │     └── gripper_action_controller
         │
         └── ROS2 Core
               ├── robot_state_publisher
               ├── joint_state_publisher_gui
               ├── rviz2
               └── xacro
```

---

## 🤖 URDF Structure

```
world (fixed)
  └── platform (fixed)
        ├── left_base_link
        │     └── left_link_1
        │           └── left_link_2
        │                 └── left_link_3
        │                       └── left_link_4
        │                             └── left_link_5
        │                                   └── left_link_6
        │                                         └── left_flange
        │                                               └── left_tool0
        │                                                     └── left_gripper_base
        │                                                           ├── left_finger_L
        │                                                           └── left_finger_R
        └── right_base_link
              └── (mirrors left arm structure)
```

---

## 🔄 Data Flow

### Joint Control Flow

```
User Command → Cartesian Controller → IK Solver → Joint Positions
     │
     ▼
JointTrajectory Action Goal → JointTrajectoryController
     │
     ▼
Command Interface → Fake Hardware → State Interface
     │
     ▼
JointStateBroadcaster → /joint_states → RViz
```

### Gripper Control Flow

```
GripperCommand Action Goal → GripperActionController
     │
     ▼
Position Command → Fake Hardware → Position State
     │
     ▼
JointStateBroadcaster → /joint_states → RViz
```

---

## 🔌 ROS2 Interfaces

### Published Topics

| Topic | Type | Publisher |
|-------|------|-----------|
| `/joint_states` | sensor_msgs/JointState | joint_state_broadcaster |
| `/robot_description` | std_msgs/String | robot_state_publisher |
| `/tf` | tf2_msgs/TFMessage | robot_state_publisher |

### Action Servers

| Action | Type | Server |
|--------|------|--------|
| `/left_arm_controller/follow_joint_trajectory` | FollowJointTrajectory | left_arm_controller |
| `/right_arm_controller/follow_joint_trajectory` | FollowJointTrajectory | right_arm_controller |
| `/left_gripper_controller/gripper_cmd` | GripperCommand | left_gripper_controller |
| `/right_gripper_controller/gripper_cmd` | GripperCommand | right_gripper_controller |

### Subscribed Topics (Cartesian Controller)

| Topic | Type | Purpose |
|-------|------|---------|
| `/left_arm/target_pose` | PoseStamped | Left arm Cartesian target |
| `/right_arm/target_pose` | PoseStamped | Right arm Cartesian target |
| `/dual_arm/sync_pose` | PoseStamped | Synchronized target |

---

## ⚙️ Controller Configuration

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100  # Hz

left_arm_controller:
  type: joint_trajectory_controller/JointTrajectoryController
  joints: [left_joint_1..6]
  command_interfaces: [position]
  state_interfaces: [position, velocity]

right_arm_controller:
  # Same as left_arm_controller with right_ prefix

left_gripper_controller:
  type: position_controllers/GripperActionController
  joint: left_gripper_finger_joint

right_gripper_controller:
  # Same as left_gripper_controller with right_ prefix
```

---

## 🐳 Docker Architecture

```
Host Machine
  │
  ├── X11 Server (/tmp/.X11-unix)
  │
  └── Docker Container (ros2-dev)
        │
        ├── /opt/ros/humble (ROS2 Humble)
        │
        ├── /ros2_ws/src (mounted volume)
        │     ├── fanuc_crx10ia_description
        │     └── fanuc_dual_arm_description
        │
        └── /ros2_ws/install (built packages)
```

