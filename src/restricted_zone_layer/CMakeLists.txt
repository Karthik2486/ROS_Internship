cmake_minimum_required(VERSION 3.5)
project(restricted_zone_layer)

# Use C++17
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(pluginlib REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav2_costmap_2d REQUIRED)
find_package(geometry_msgs REQUIRED)

include_directories(include)

# Build the plugin library
add_library(${PROJECT_NAME} SHARED
  src/restricted_zone_layer.cpp
)

ament_target_dependencies(${PROJECT_NAME}
  rclcpp
  pluginlib
  nav2_costmap_2d
  geometry_msgs
)

# ✅ Register the plugin with pluginlib
pluginlib_export_plugin_description_file(nav2_costmap_2d restricted_zone_layer.xml)

# Install library
install(TARGETS ${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

# Install include directory
install(DIRECTORY include/
  DESTINATION include/
)

# Install plugin XML and package.xml
install(FILES restricted_zone_layer.xml package.xml
  DESTINATION share/${PROJECT_NAME}
)

# Export dependencies
ament_export_dependencies(pluginlib nav2_costmap_2d)
ament_package()

