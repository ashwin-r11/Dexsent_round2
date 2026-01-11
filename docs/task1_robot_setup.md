# Task 1: Robot Setup & Gripper Integration

Complete guide for loading the Fanuc CRX-10iA robot with Robotiq gripper into ROS2.

---

## 🎯 Objectives

- [x] Load Fanuc CRX-10iA URDF into ROS2
- [x] Display robot in RViz
- [x] Enable joint trajectory execution using ros2_control
- [x] Attach Robotiq 2F-85 gripper
- [x] Support FollowJointTrajectory action

---

## 📁 File Structure

```
src/fanuc_crx10ia_description/
├── urdf/
│   └── crx10ial.urdf           # Original Fanuc URDF
├── meshes/crx10ial/
│   ├── visual/                  # Visual meshes (.stl)
│   └── collision/               # Collision meshes (.stl)
├── config/
│   └── controllers.yaml         # Single arm controller config
├── launch/
│   ├── display.launch.py        # RViz display
│   └── bringup.launch.py        # ros2_control bringup
├── rviz/
│   └── crx10ial.rviz
├── package.xml
└── CMakeLists.txt
```

---

## 🔧 Implementation Details

### 1. URDF Loading

The original Fanuc CRX-10iA URDF was obtained from:
```
https://github.com/Daniella1/urdf_files_dataset/tree/main/urdf_files/ros-industrial
```

Modified to add:
- ros2_control hardware interface block
- Robotiq gripper links and joints

### 2. ros2_control Integration

**Hardware Interface:**
```xml
<ros2_control name="CRX10iASystem" type="system">
  <hardware>
    <plugin>fake_components/GenericSystem</plugin>
  </hardware>
  <!-- Joint definitions -->
</ros2_control>
```

**Controllers:**
- `joint_state_broadcaster` - Publishes joint states
- `arm_controller` - JointTrajectoryController for 6 arm joints
- `gripper_controller` - GripperActionController for gripper

### 3. Gripper Integration

**Robotiq 2F-85 Gripper** integrated via URDF:

```
gripper_base_link
    ├── gripper_left_finger_link (prismatic joint)
    └── gripper_right_finger_link (prismatic joint, mimic)
```

- `gripper_finger_joint` - Main control joint (position: 0.0 closed, 0.04 open)
- Right finger uses `mimic` joint to mirror left finger

---

## 🚀 Usage

### Display in RViz (with sliders)

```bash
ros2 launch fanuc_crx10ia_description display.launch.py
```

### Launch with ros2_control

```bash
ros2 launch fanuc_crx10ia_description bringup.launch.py
```

---

## 🔌 Topics & Actions

| Topic/Action | Type | Description |
|--------------|------|-------------|
| `/joint_states` | sensor_msgs/JointState | Current joint positions |
| `/robot_description` | std_msgs/String | URDF string |
| `/arm_controller/follow_joint_trajectory` | FollowJointTrajectory | Arm trajectory action |
| `/gripper_controller/gripper_cmd` | GripperCommand | Gripper control action |

---

## ✅ Verification

1. **RViz Display** - Robot visible with all links
2. **Joint Movement** - Sliders move robot joints
3. **TF Tree** - All transforms published correctly
4. **Controller State** - `ros2 control list_controllers` shows active controllers

---

## 📝 Notes

- Uses `fake_components/GenericSystem` for simulation (no real hardware)
- Gripper geometry is simplified (boxes instead of actual Robotiq meshes)
- Joint limits match Fanuc CRX-10iA specifications

