cmake_minimum_required(VERSION 3.8)
project(fanuc_dual_arm_description)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

# Install directories
install(DIRECTORY urdf config launch rviz
  DESTINATION share/${PROJECT_NAME}
)

# Install Python scripts as executables
install(PROGRAMS
  scripts/cartesian_controller.py
  scripts/sync_motion_demo.py
  scripts/pick_place_demo.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
