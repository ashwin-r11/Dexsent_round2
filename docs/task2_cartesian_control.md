# Task 2: Dual-Arm Cartesian Control

Complete guide for implementing dual-arm Cartesian control with synchronized motion.

---

## 🎯 Objectives

- [x] Mount two CRX-10iA robots at 45° angles
- [x] Implement Cartesian control using ros2_control
- [x] Coordinate both arms synchronously

---

## 📁 File Structure

```
src/fanuc_dual_arm_description/
├── urdf/
│   ├── dual_arm.urdf.xacro      # Dual-arm assembly
│   └── crx10ia_macro.xacro      # Reusable arm macro
├── config/
│   └── dual_arm_controllers.yaml # Controllers for both arms
├── launch/
│   ├── display.launch.py         # RViz with sliders
│   ├── dual_arm_bringup.launch.py # ros2_control bringup
│   └── dual_arm_cartesian.launch.py # Full Cartesian control
├── scripts/
│   ├── cartesian_controller.py   # IK-based Cartesian control
│   ├── sync_motion_demo.py       # Synchronized motion demo
│   └── pick_place_demo.py        # Pick-and-place with grippers
├── rviz/
│   └── dual_arm.rviz
├── package.xml
└── CMakeLists.txt
```

---

## 🔧 Implementation Details

### 1. Dual-Arm Mounting

Both robots mounted on a platform with 45° outward roll:

```xml
<!-- Left arm: +45° roll -->
<origin xyz="0 -0.15 0" rpy="0.785 0 0"/>

<!-- Right arm: -45° roll -->
<origin xyz="0 0.15 0" rpy="-0.785 0 0"/>
```

This creates a "V" shape when viewed from the front.

### 2. Xacro Macro

Single arm defined as reusable macro with prefix parameter:

```xml
<xacro:macro name="crx10ia_arm" params="prefix parent_link *origin">
  <!-- All links and joints use ${prefix} -->
</xacro:macro>
```

Instantiated twice:
- `left_` prefix for left arm
- `right_` prefix for right arm

### 3. Cartesian Control

**Architecture:**
```
Cartesian Pose (geometry_msgs/PoseStamped)
         ↓
   cartesian_controller.py (IK solver)
         ↓
   JointTrajectoryController
         ↓
   Robot Joints
```

**IK Approach:**
- Simple geometric IK for demo purposes
- Production use would integrate KDL or MoveIt IK

### 4. Synchronized Motion

**Mirroring Strategy:**
- Define motion for left arm
- Mirror joint_1 for right arm: `right_j1 = -left_j1`
- Other joints: same values

**Delta-based Motion:**
- Store neutral pose values
- Apply deltas for symmetric movement

---

## 🚀 Usage

### Launch Cartesian Control System

```bash
ros2 launch fanuc_dual_arm_description dual_arm_cartesian.launch.py
```

### Run Synchronized Demo

```bash
python3 /ros2_ws/src/fanuc_dual_arm_description/scripts/sync_motion_demo.py
```

### Run Pick-and-Place Demo

```bash
python3 /ros2_ws/src/fanuc_dual_arm_description/scripts/pick_place_demo.py
```

---

## 🔌 Topics & Actions

| Topic/Action | Type | Description |
|--------------|------|-------------|
| `/left_arm/target_pose` | PoseStamped | Left arm Cartesian target |
| `/right_arm/target_pose` | PoseStamped | Right arm Cartesian target |
| `/dual_arm/sync_pose` | PoseStamped | Synchronized mirrored motion |
| `/left_arm_controller/follow_joint_trajectory` | FollowJointTrajectory | Left arm trajectory |
| `/right_arm_controller/follow_joint_trajectory` | FollowJointTrajectory | Right arm trajectory |
| `/left_gripper_controller/gripper_cmd` | GripperCommand | Left gripper control |
| `/right_gripper_controller/gripper_cmd` | GripperCommand | Right gripper control |

---

## 🎮 Demo Sequences

### sync_motion_demo.py
1. NEUTRAL position
2. Arms UP
3. Arms FORWARD
4. Arms SPREAD
5. Arms INWARD
6. Return to NEUTRAL

### pick_place_demo.py
1. HOME + OPEN grippers
2. APPROACH workpiece
3. GRIP (close grippers)
4. LIFT
5. MOVE to side
6. LOWER
7. RELEASE (open grippers)
8. RETRACT
9. Return HOME

---

## ✅ Verification

1. **Symmetric Motion** - Both arms mirror each other
2. **Gripper Control** - Fingers open/close correctly
3. **No Collision** - Arms stay separated
4. **Smooth Trajectories** - No jerky movement

---

## 📝 Design Decisions

| Decision | Rationale |
|----------|-----------|
| Simple geometric IK | Easy to explain in interview, works for demo |
| Delta-based movement | Ensures symmetric motion from neutral pose |
| Separate arm controllers | Standard ros2_control pattern |
| GripperActionController | Native ros2_controllers plugin |

---

## 🔮 Production Improvements

For production deployment:
1. Replace geometric IK with KDL or MoveIt IK
2. Add collision checking
3. Implement trajectory optimization
4. Add force feedback for grippers

