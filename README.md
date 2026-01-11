# Fanuc CRX-10iA Dual-Arm ROS2 System

A complete ROS2 Humble implementation of a dual-arm robotic system using two Fanuc CRX-10iA collaborative robots with Robotiq grippers.

![ROS2 Humble](https://img.shields.io/badge/ROS2-Humble-blue)
[![ROS2 Build & Test](https://github.com/ashwin-r11/Dexsent_round2/actions/workflows/ros2-ci.yml/badge.svg)](https://github.com/ashwin-r11/Dexsent_round2/actions/workflows/ros2-ci.yml)
![License](https://img.shields.io/badge/License-BSD--3--Clause-green)

## Version History / Milestones

| Tag          | Description                                        | View Code                 |
| ------------ | -------------------------------------------------- | ------------------------- |
| `v1.0-task1` | Task 1 Complete: Robot Setup & Gripper Integration | `git checkout v1.0-task1` |
| `v2.0-task2` | Task 2 Complete: Dual-Arm Cartesian Control        | `git checkout v2.0-task2` |
| `HEAD`       | Latest: Documentation, CI, and refinements         | `git checkout master`     |

**For reviewers:** Use tags to view the code at each milestone completion.

## Project Overview

This project implements a dual-arm robotic workcell with:
- Two Fanuc CRX-10iA robots mounted at 45° angles
- Robotiq 2F-85 grippers on each arm
- ros2_control integration with fake hardware
- Cartesian control capability
- Synchronized dual-arm motion

## Demo Videos

### Task 1: Single Arm with Gripper
https://github.com/user-attachments/assets/d5566bed-1d36-4f47-a5c9-10631cfb67cf

[Download Task 1 Demo](docs/vids/task1%20demo.mp4)

### Task 2: Dual-Arm Synchronized Motion
https://github.com/user-attachments/assets/0d8bb7f4-822b-4086-a894-8e726680761c

[Download Working Demo](docs/vids/working%20demo.mp4)

---

## Repository Structure

```
Dexsent_round2/
├── .github/workflows/
│   └── ros2-ci.yml              # GitHub Actions CI/CD
├── src/
│   ├── fanuc_crx10ia_description/   # Single arm URDF + meshes
│   └── fanuc_dual_arm_description/  # Dual-arm system + control
├── docs/
│   ├── imgs/                    # Reference images
│   ├── vids/                    # Demo videos
│   ├── references/              # Research papers
│   ├── report.pdf               # Technical report (1-2 pages)
│   ├── task1_robot_setup.md     # Task 1 documentation
│   ├── task2_cartesian_control.md   # Task 2 documentation
│   ├── architecture.md          # System architecture
│   ├── troubleshooting.md       # Common issues & fixes
│   ├── flex.md                  # Project highlights
│   └── my_exp.md                # Development experience
├── docker-compose.yml
├── Dockerfile
├── docker-entrypoint.sh
└── README.md
```

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- X11 display server (for RViz)

### 1. Clone & Build

```bash
git clone https://github.com/ashwin-r11/Dexsent_round2.git

cd  Dexsent_round2

# Allow X11 forwarding
xhost +local:docker

# Start Docker environment
docker compose up -d
docker compose exec ros2-dev bash
```

### 2. Build Workspace

```bash
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

### 3. Launch

#### Task 1: Single Arm with Gripper

**Display Mode (with joint sliders):**
```bash
ros2 launch fanuc_crx10ia_description display.launch.py
```

**Control Mode (with ros2_control):**
```bash
ros2 launch fanuc_crx10ia_description bringup.launch.py
```

**Run Demo:**
```bash
# In another terminal
python3 /ros2_ws/src/fanuc_crx10ia_description/scripts/trajectory_demo.py
```

---

#### Task 2: Dual-Arm with Cartesian Control

**Display Mode (with joint sliders):**
```bash
ros2 launch fanuc_dual_arm_description display.launch.py
```

**Control Mode (with Cartesian controller):**
```bash
ros2 launch fanuc_dual_arm_description dual_arm_cartesian.launch.py
```

**Run Demo:**
```bash
# In another terminal
python3 /ros2_ws/src/fanuc_dual_arm_description/scripts/pick_place_demo.py
```

---

## Tasks Completed

### Task 1: Robot Setup & Gripper Integration
- Fanuc CRX-10iA loaded into ROS2
- Robot displayed in RViz
- Joint trajectory execution via ros2_control
- Robotiq gripper integrated
- FollowJointTrajectory support

See [Task 1 Documentation](docs/task1_robot_setup.md)

### Task 2: Dual-Arm Cartesian Control
- Two robots mounted at 45° angles
- Cartesian control implemented
- Synchronized dual-arm motion
- Pick-and-place demo with gripper control

See [Task 2 Documentation](docs/task2_cartesian_control.md)

📄 **[Technical Report (PDF)](docs/report.pdf)** — Architecture, challenges, solutions, and design decisions

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ROS2 Humble                          │
├─────────────────────────────────────────────────────────┤
│     RViz2          Controller Manager     Cartesian     │
│                                           Controller    │
├─────────────────────────────────────────────────────────┤
│                     ros2_control                        │
│   Left Arm Controller    │    Right Arm Controller      │
│   Left Gripper           │    Right Gripper             │
├─────────────────────────────────────────────────────────┤
│              Fake Hardware Interface                    │
│           (fake_components/GenericSystem)               │
└─────────────────────────────────────────────────────────┘
```

See [Full Architecture](docs/architecture.md)

---

## Packages

| Package                      | Description                               |
| ---------------------------- | ----------------------------------------- |
| `fanuc_crx10ia_description`  | Single arm URDF, meshes, and basic launch |
| `fanuc_dual_arm_description` | Dual-arm URDF, controllers, demos         |

---

## Available Launch Files

| Launch File                    | Description                                    |
| ------------------------------ | ---------------------------------------------- |
| `display.launch.py`            | RViz + joint_state_publisher_gui (for testing) |
| `dual_arm_bringup.launch.py`   | ros2_control without Cartesian node            |
| `dual_arm_cartesian.launch.py` | Full system with Cartesian control             |

---

## Controller Configuration

Defined in `dual_arm_controllers.yaml`:
- `joint_state_broadcaster`
- `left_arm_controller` (JointTrajectoryController)
- `right_arm_controller` (JointTrajectoryController)
- `left_gripper_controller` (GripperActionController)
- `right_gripper_controller` (GripperActionController)

---

## Design Decisions

| Decision           | Rationale                                               |
| ------------------ | ------------------------------------------------------- |
| Fake Hardware      | Using `fake_components/GenericSystem` for simulation    |
| Simple IK          | Geometric IK for demo (production would use KDL/MoveIt) |
| Symmetric Mounting | 45° roll for each arm creating V-shape                  |
| Delta-based Motion | Demo uses deltas from neutral pose for symmetric motion |

---

## References

### Environment Setup
- [Docker with ROS - ROS Wiki](https://wiki.ros.org/docker/Tutorials/Docker)
- [Docker Containers Setup - MoveIt](https://moveit.picknik.ai/humble/doc/how_to_guides/how_to_setup_docker_containers_in_ubuntu.html)

### Dual-Arm Robotics
- [Dual-Arm Jacobian Comparison (PDF)](docs/references/dual-arm-compare-jacobian_cis-ram_small.pdf)
  - *Authors: F. Caccavale, C. Natale, B. Siciliano, L. Villani - IEEE CIS-RAM*

#### Mounting Reference Sketch
*Sketch by: Ashwin R*

![Dual-Arm Mounting Sketch](docs/imgs/Note_sketches.jpeg)

### Motion Planning
- [MoveIt 2 Concepts](https://moveit.picknik.ai/main/doc/concepts/concepts.html)
- [ROS2 Interfaces](https://docs.ros.org/en/humble/Concepts/Basic/About-Interfaces.html)

### Grippers & End Effectors
- [Robotic Grippers Research (PDF)](https://rjwave.org/ijedr/papers/IJEDR1601080.pdf)

### Robot Specifications
- [Fanuc CRX-10iA Specs](https://www.fanuc.eu/uk/en/robots/robot-filter-page/collaborative-robots/crx-10ia)
- [ros2_control Documentation](https://control.ros.org/humble/)
- [ROS2 Humble Docs](https://docs.ros.org/en/humble/)

---

## License

BSD-3-Clause

---

## Author

**Ashwin R**

Developed for DexSent Robotics Technical Screening
