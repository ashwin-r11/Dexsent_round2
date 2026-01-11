# Troubleshooting Guide

Common issues and solutions for the Fanuc CRX-10iA Dual-Arm ROS2 System.

---

## Docker & Environment

### RViz/GUI not displaying

**Symptom:** RViz opens but window doesn't appear, or errors about display.

**Solution:**
```bash
# On host machine (outside Docker)
xhost +local:docker

# Verify DISPLAY variable in Docker
echo $DISPLAY  # Should show :0 or :1
```

### `ros2: command not found`

**Symptom:** ROS2 commands fail.

**Solution:**
```bash
source /opt/ros/humble/setup.bash
source /ros2_ws/install/setup.bash
```

### Terminals not communicating

**Symptom:** Topics published in one terminal aren't seen in another.

**Solution:** Ensure both terminals are in the same Docker context:
```bash
docker context use default
docker compose exec ros2-dev bash
```

---

## Build Issues

### Package not found after build

**Symptom:** `ros2 launch` can't find package.

**Solution:**
```bash
source /ros2_ws/install/setup.bash
```

### Launch file not found

**Symptom:** New launch file isn't recognized.

**Solution:** Rebuild the package:
```bash
colcon build --packages-select fanuc_dual_arm_description
source install/setup.bash
```

### Python script not executable

**Symptom:** `ros2 run` says "No executable found".

**Solution:**
```bash
chmod +x /ros2_ws/src/fanuc_dual_arm_description/scripts/*.py
colcon build --packages-select fanuc_dual_arm_description
```

---

## URDF & Visualization

### Robot floating in RViz

**Symptom:** Robot appears above the ground plane.

**Solution:** Check the `world` to `platform` joint Z offset in URDF.

### Robot not visible in RViz

**Symptom:** TF tree visible but no robot model.

**Solution:** 
1. Add RobotModel display in RViz
2. Set "Description Topic" to `/robot_description`
3. Set "Fixed Frame" to `world`

---

## Controller Issues

### Controller fails to load

**Symptom:** Error loading controller.

**Solution:** Check controller config in `dual_arm_controllers.yaml`:
- Joint names must match URDF
- Controller type must be correct

### Gripper not moving

**Symptom:** Gripper commands sent but no movement.

**Solution:** Ensure gripper controllers are spawned in launch file:
```python
ExecuteProcess(
    cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'left_gripper_controller'],
)
```

---

## Demo Issues

### Arms colliding with each other

**Symptom:** Robot arms pass through each other.

**Solution:** Use smaller delta values in demo scripts. Keep arms on their respective sides.

### Asymmetric motion

**Symptom:** Left and right arms don't mirror properly.

**Solution:** Use delta-based motion from neutral pose. Mirror joint_1 for right arm.

---

## Quick Checks

```bash
# Check controllers are active
ros2 control list_controllers

# Check topics
ros2 topic list

# Check TF tree
ros2 run tf2_tools view_frames

# Test gripper manually
ros2 action send_goal /left_gripper_controller/gripper_cmd control_msgs/action/GripperCommand "{command: {position: 0.04}}"
```

---
