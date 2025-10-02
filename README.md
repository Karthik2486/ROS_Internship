# ROS_Internship
# ROS Internship – Deliverable 3: Autonomous Patrol and Navigation  

This deliverable demonstrates **autonomous patrol and navigation** using TurtleBot3 in Gazebo with **Navigation2 (Nav2)** stack.  
The robot performs looped perimeter patrols and waypoint-based navigation, maintaining safety and path efficiency.  

---

## ✅ Features Implemented
- **Nav2 with DWB/TEB planners**
- **Waypoint patrol & pillar loop navigation**
- **AMCL localization with map server**
- **Patrol rerouting via RViz (clicked points)**
- **ROS2 bag recording & replay for evaluation**

---

## 🚀 Running Autonomous Patrol
1. Launch Gazebo simulation with TurtleBot3 world:
   ```bash
   ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
