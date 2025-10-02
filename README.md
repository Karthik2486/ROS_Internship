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
2. Launch Navigation2, bring up the Nav2 stack with AMCL and costmaps:
   ```bash
   ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True
3. Run waypoint follower with YAML waypoints:
   ```bash
   ros2 run waypoint_helper follow_waypoints --ros-args -p waypoints_file:=$HOME/geckon_ws/saved_maps/pillar_loop.yaml

This loads:
   map_server
   amcl (localization)
   planner_server
   controller_server
   waypoint_follower
   RViz with Nav2 panel

Using Pre-Recorded Bag File
A bag file of the patrol run has already been recorded and provided.
To replay and view results in RViz:
Step 1: Launch Nav2 with sim time enabled
    ```bash
    ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True

Step 2: Ensure use_sim_time is set
Run these commands so all nodes use the simulated clock:
    ```bash
    ros2 param set /rviz2 use_sim_time true
    ros2 param set /amcl use_sim_time true
    ros2 param set /map_server use_sim_time true
    ros2 param set /waypoint_follower use_sim_time true
5. Replay the bag with clock
    ```bash
    ros2 bag play ~/geckon_ws/bags/autonav_nav2 --clock
📌 Notes:
The patrol loop waypoints are stored in saved_maps/pillar_loop.yaml.
This deliverable focuses on successful autonomous patrol navigation with Nav2.
