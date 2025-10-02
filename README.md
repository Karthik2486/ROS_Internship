# ROS_Internship

# ROS Internship – Deliverable 3: Autonomous Patrol and Navigation

This deliverable demonstrates **autonomous patrol and navigation** using TurtleBot3 in Gazebo with the **Navigation2 (Nav2) stack**.  
The robot performs looped perimeter patrols and waypoint-based navigation while maintaining safety and path efficiency.

---

## ✅ Features Demonstrated
- **Nav2 with DWB planner**
- **Waypoint patrol navigation (pillar loop)**
- **AMCL localization with saved map**
- **Replay of pre-recorded bag file for evaluation**

---

## 🚀 Running Autonomous Patrol

### Step 1 – Launch Gazebo Simulation
Start the TurtleBot3 simulation in Gazebo:

      
      export TURTLEBOT3_MODEL=burger
      ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
### Step 2 – Launch Navigation2 with Map
Bring up the Nav2 stack with AMCL, costmaps, and RViz:
     
      
      ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True
This loads:
map_server
amcl (localization)
planner_server
controller_server
waypoint_follower
rviz2 with Nav2 panel

### Step 3 – Run Waypoint Navigation
(a) Basic Navigation Goal
Set a Nav2 goal manually in RViz:
 - Use the Nav2 Goal button to click a target pose.
 - Robot will navigate to the selected position.

(b) Waypoint Patrol (Square / Loop)
Run waypoints defined in waypoints.yaml:
      
      
      ros2 run waypoint_helper follow_waypoints --ros-args -p waypoints_file:=$HOME/geckon_ws/saved_maps/waypoints.yaml
(c) Pillar Loop Patrol
Run patrol waypoints around a pillar structure using pillar_loop.yaml:

      
      ros2 run waypoint_helper follow_waypoints --ros-args -p waypoints_file:=$HOME/geckon_ws/saved_maps/pillar_loop.yaml

📂 Replay Pre-Recorded Bag File

A bag file of the patrol run has already been recorded and stored in ~/geckon_ws/bags/autonav_nav2.
Follow these steps to visualize results in RViz:

Step 1 – Launch Nav2 with sim time enabled

      
      ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True
Step 2 – Ensure use_sim_time is set
Run these commands so all nodes sync with the bag’s clock:

      
      ros2 param set /rviz2 use_sim_time true
      ros2 param set /amcl use_sim_time true
      ros2 param set /map_server use_sim_time true
      ros2 param set /waypoint_follower use_sim_time true
Step 3 – Replay the bag

      
      ros2 bag play ~/geckon_ws/bags/autonav_nav2 --clock

🎯 Expected Results

The robot performs autonomous waypoint patrol and pillar loop navigation.
RViz shows:
**Map with AMCL localization
**Global and local costmaps
**TF transforms
**Patrol path execution
**When replaying the bag file, the patrol loop is reproduced exactly as recorded.

📌 Notes
Waypoints are stored in ~/geckon_ws/saved_maps/waypoints.yaml and ~/geckon_ws/saved_maps/pillar_loop.yaml.
Deliverable 3 focuses on autonomous patrol navigation with Nav2 and evaluation via bag replay.
