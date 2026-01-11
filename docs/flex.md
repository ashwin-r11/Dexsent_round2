# Project Highlights

---

## 1. Collision-Free Movement
The robot arms respect each other's space — no passing through each other!

![Gripper Collision Prevention](/docs/imgs/gripper_collision_closeup.png)

---

## 2. Simple and Clean Architecture
Minimal dependencies: Just MoveIt2 and ros2_control. No unnecessary complexity.

---

## 3. Dockerized Development Environment
Complete Docker setup with:
- Pre-configured ROS2 Humble environment
- X11 forwarding for GUI applications (RViz)
- Volume mounting for live code editing
- Reproducible builds across any machine

---

## 4. Hand-Drawn Reference Sketches
Created custom reference sketches for the dual-arm mounting configuration.

![Mounting Sketches](/docs/imgs/Note_sketches.jpeg)

---

## 5. Xacro-Based Modular URDF
- Reusable arm macro with prefix parameter
- Easy to extend for different configurations
- Clean separation of robot definition and scene setup

---

## 6. Well-Organized Repository
- Clear folder structure (src, docs, config)
- Separate documentation for each task
- Architecture diagrams included

---

## 7. Version-Tagged Milestones
Git tags for each task completion:
- `v1.0-task1` — Robot setup complete
- `v2.0-task2` — Dual-arm control complete

---

## 8. AI-Assisted Development Guidelines
Established clear guidelines for AI-assisted development to ensure code quality and security.

See [Development Guidelines](docs/llm_workflow.txt)

---

## 9. CI/CD with GitHub Actions
Automated pipeline that tests:
- Docker build
- ROS2 workspace compilation
- URDF parsing validation
- Controller configuration check

Check the **Actions** tab in the repository!

---

## 10. Comprehensive Documentation
- README with quick start guide
- Task-specific documentation
- Architecture overview
- Troubleshooting notes

---
