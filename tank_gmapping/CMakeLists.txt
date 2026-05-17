cmake_minimum_required(VERSION 3.8)
project(tank)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Tìm gói build của ROS 2
find_package(ament_cmake REQUIRED)

# Cài đặt (copy) các thư mục chứa file cấu hình, mô hình và script vào không gian làm việc
install(DIRECTORY
  launch
  meshes
  urdf
  config
  worlds
  DESTINATION share/${PROJECT_NAME}
)

# Khai báo file Python điều khiển để ROS 2 có thể chạy được qua lệnh `ros2 run`
install(PROGRAMS
  scripts/keyboard_control.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()