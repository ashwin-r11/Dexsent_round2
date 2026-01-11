# My Honest Experience While Doing These Tasks

## Intro

Ahem ahem! So yeah, it's been one hell of a journey doing these tasks. Oof!

So basically, I'm a CSE core student with specialization in Iot and automation, so I have exposure to os, networking, AI/ML,embedded systems,iot and all that jazz! But still, the thought of having your code interact with the physical world seemed so fun and made me literally work on this for days and days! I've practically lost track of time! (Worked nearly 4+ hours in one sitting) [Sounds exaggerated, right? Trust me, I'm still unable to believe it myself, but that's the reality!]

## Initial Run

Since my exposure to robotics is a bit low compared to my AI/ML system engineering background, I found it a bit hard to get started with this task. Couldn't wrap my head around the concepts of MoveIt and ROS initially — it all seemed a bit complex to me. Then I broke it into pieces and started learning them one by one. Which was totally worth it!

## Key Mantras I Said to Myself

1. Don't expect to learn everything within 72 hours and become practically good at it.
2. Do what you can and make it the best, rather than making a whole but fragile prototype.
3. Concepts can be studied (only if they're useful for the tasks! If something looks fancy or cool, note it and learn it later, but don't expect to learn all of it!)
4. Time/work tends to compromise on quality! So try to disrupt this relation using AI to practically aim for the ideal.
5. No ego in not knowing something! Just ask! And don't overclaim — it is what it is!

## List of Mistakes I Made (So You Don't Have To)

1. Trying to straight away jump into tasks, only to mess up by corrupting the Docker image and past progress (and Git wasn't initialized either!)
2. Not looking into the [visual reference](docs/references/dual-arm-compare-jacobian_cis-ram_small.pdf) (the font color of the link in the given Notion site is invisible and hard to spot!)
3. Messed up with gripper and arms getting into each other! (Like, it doesn't care — it just goes through each other!)

## Issues Encountered (Technical Format)

### Docker & Environment
- **X11 Display Forwarding** — RViz/GUI not displaying initially, needed `xhost +local:docker` and correct `DISPLAY` variable
- **Docker Context Mismatch** — Terminal 1 was bash vs Terminal 2 was docker-desktop, so ROS topics weren't communicating between them
- **ROS2 setup not sourced** — Commands failing with `ros2: command not found`, needed `source /opt/ros/humble/setup.bash`

### URDF & Robot Setup
- **Robot "floating" in RViz** — Initial URDF had robot base too high, needed to adjust Z offset
- **Arm mounting orientation** — Multiple iterations to get the 45° angles correct (tried pitch, then roll, swapped signs multiple times)
- **Side-by-side vs front-back placement** — Changed from X-axis offset to Y-axis offset for proper side-by-side mounting

### Gripper Issues
- **Gripper fingers overlapping** — When closing, fingers merged into each other; axis directions were wrong, needed to swap axis and reduce origin offset
- **Gripper controller not spawning** — `dual_arm_cartesian.launch.py` didn't include gripper controller spawning initially

### Cartesian Control & Demo
- **Simplified IK producing asymmetric motion** — First IK approach gave different poses for left/right arms
- **Arms colliding with each other** — Demo movements were too aggressive, had to reduce delta values
- **Python scripts not executable** — `chmod +x` needed but was run on host, not visible in Docker

### Scripts & Launch
- **Scripts not found by `ros2 run`** — CMakeLists.txt needed `install(PROGRAMS ...)` for Python scripts
- **Launch file not installed** — New launch file created after build, needed rebuild

### Initial Pose Configuration
- **Neutral pose not matching** — Multiple iterations with Joint State Publisher GUI to get the desired symmetric neutral pose

---

*Written with honesty and a lot of caffeine ☕*
