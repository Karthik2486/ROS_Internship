# ROS_Internship

# Deliverable 1: Environment Mapping & Localisation

This deliverable demonstrates **environment mapping and localisation** using the standard **TurtleBot3 stack** with ROS 2 Humble.  
Since TurtleBot3 already provides official packages for SLAM and Navigation2, the goal is to configure, test, and show a working workflow for:  

- **SLAM (Cartographer)** for map building  
- **Persistent map saving** (YAML + PGM)  
- **Localisation with AMCL**  
- **Re-localisation after reboot or drift**  

---

## 🚀 Running the Mapping & Localisation

### 1. Launch Gazebo Simulation
Start the default TurtleBot3 world in Gazebo:
            
            
            export TURTLEBOT3_MODEL=burger
            ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
### 2. Run Cartographer SLAM
Bring up Cartographer to perform SLAM while driving the robot:

            
            ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
Drive the robot manually to explore the world:

            
            ros2 run turtlebot3_teleop teleop_keyboard
As you move the robot, a 2D occupancy grid map will be built in RViz.

### 3. Save the Persistent Map
Once mapping is complete, save the map to disk:

            
            ros2 run nav2_map_server map_saver_cli -f ~/geckon_ws/saved_maps/my_map

This produces:
- my_map.pgm (map image)
- my_map.yaml (map metadata)

### 4. Launch Navigation with AMCL
Close Cartographer, then start Navigation2 with the saved map:

            
            ros2 launch turtlebot3_navigation2 navigation2.launch.py \
            use_sim_time:=True map:=$HOME/geckon_ws/saved_maps/my_map.yaml

✅ Deliverable Objectives Met
- Mapping: Achieved using Cartographer.
- Persistent map: Saved with map_saver_cli.
- Localisation: Achieved with AMCL on the saved map.
- Re-localisation: Demonstrated with RViz "2D Pose Estimate.
---


# Deliverable 2 — Restricted Zones for Nav2 (ROS 2 Humble)

## 1. Objective

Implement “restricted zones” that the robot must not enter while using the standard Nav2 stack. The solution integrates with Nav2 costmaps so that planners automatically avoid operator-defined polygons on the map. The implementation must be observable in RViz and provide reproducible evidence (topics, nodes, graphs, and recordings).

---

## 2. What was implemented (high-level)

1. **A Nav2 Costmap Plugin (`restricted_zone_layer`)**  
   - C++ plugin for `nav2_costmap_2d`.  
   - Subscribes to a polygon topic and rasterizes those polygons into the costmap as lethal cells (cost=254).  
   - Works with both **global** and **local** costmaps so the global planner and the controller treat these regions as obstacles and reroute.

2. **A Visualization Node (`restricted_zone_viz`)**  
   - Python node that consumes the same polygon input and publishes a `visualization_msgs/Marker` for RViz.  
   - Purpose: (a) operator feedback that the polygon was received in the intended frame (`map`) and (b) evidence for the demo and supervisor.  
   - This node does not influence planning directly; it only visualizes.

3. **Nav2 configuration (`restricted_nav2_params.yaml`)**  
   - Adds the plugin to the `plugins` list of both local and global costmaps.  
   - Sets plugin-specific parameters (topic name, enabled flag, lethal cost).

This approach uses standard Nav2 extension points, so we keep the built-in planners/controllers and simply feed them richer costmaps. It avoids custom planners and remains compatible with other layers (static/obstacle/inflation).

---

## 3. Why a costmap plugin (and why it works)

- **Nav2 planning is costmap-driven.** Global and local planners (e.g., `Navfn`, `Smac`, `DWB`) read from costmaps; cells with high/lethal cost are effectively “blocked.”  
- **Plugins participate in costmap composition.** At every update, the costmap combines multiple layers (static, obstacle, inflation, custom). Our `restricted_zone_layer` injects lethal costs inside any polygon, so those areas become non-traversable.  
- **Planner-agnostic.** Because planners only see the final costmap, they naturally avoid restricted regions without modifying planner code.

---

## 4. What is `restricted_zone_layer`

- A **nav2_costmap_2d** layer plugin written in C++.  
- Subscribes to: `/restricted_zone/polygons` (`geometry_msgs/PolygonStamped`).  
- For each polygon, it:
  1. Transforms coordinates in the costmap’s frame (assumed `map` for global, `odom`/`map` for local as configured).  
  2. Rasterizes the polygon footprint into grid indices.  
  3. Sets those grid cells’ cost to `LETHAL_OBSTACLE` (defaults to 254).  
- Exposes parameters via YAML:
  - `enabled` (bool)
  - `zone_topic` (string, default `/restricted_zone/polygons`)
  - `lethal_cost` (int, default 254)

---

## 5. What is `restricted_zone_viz` (and why we needed it)

- A **visualization-only** node that aids development, debugging, and demonstration.  
- Subscribes to the same polygon topic and publishes:
  - `/restricted_zone/markers` (`visualization_msgs/Marker`), a closed red polygon line/filled shape in the `map` frame.  
- Reasons to include it:
  - Confirm the publisher is sending polygons in the correct frame and shape.
  - Confirm timing and persistence (e.g., if the polygon is latched or republished).
  - Provide a clear RViz overlay for supervisors and reviewers.

---

## 6. Simplified data flow

```

User / Tools (publish PolygonStamped)
|
v
/ restricted_zone / polygons  (geometry_msgs/PolygonStamped)
|                                 |
|                                 +--> restricted_zone_viz
|                                       - Subscribes to polygons
|                                       - Publishes /restricted_zone/markers (Marker)
|
+--> restricted_zone_layer (costmap plugin)
- Subscribes to polygons
- Writes lethal cells into costmap
|
v
Nav2 Global/Local Costmaps  --->  Nav2 Planner/Controller  ---> Robot avoids restricted zones

````

Key topics:
- **Input polygon**: `/restricted_zone/polygons`  
- **Visualization marker**: `/restricted_zone/markers`

---

## 7. Files and locations (summary)

- `src/restricted_zone_layer/src/restricted_zone_layer.cpp`  
- `src/restricted_zone_layer/include/restricted_zone_layer/restricted_zone_layer.hpp`  
- `src/restricted_zone_layer/restricted_zone_layer.xml`  
- `src/restricted_zone_layer/CMakeLists.txt`  
- `src/restricted_zone_layer/package.xml`  
- `src/restricted_zone_layer/config/restricted_nav2_params.yaml`  
- `src/restricted_zone_viz/restricted_zone_viz/zone_viz.py`  
- `src/restricted_zone_viz/package.xml`, `setup.py`, `resource/restricted_zone_viz`

---

## 8. Step-by-step: build, launch, publish polygons, verify

> Assumptions: ROS 2 Humble installed; TurtleBot3 packages available; workspace is `~/geckon_ws`.

### 8.1 Build and source
```bash
cd ~/geckon_ws
rm -rf build install log
colcon build --symlink-install --packages-select restricted_zone_layer restricted_zone_viz
source /opt/ros/humble/setup.bash
source ~/geckon_ws/install/setup.bash
````

### 8.2 Launch Gazebo world (if sim)

```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

### 8.3 Launch Nav2 with restricted zone layer

```bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  use_sim_time:=True \
  params_file:=$HOME/geckon_ws/src/restricted_zone_layer/config/restricted_nav2_params.yaml
```

**Notes about the YAML**
Your `restricted_nav2_params.yaml` must include the plugin in both **local** and **global** costmap `plugins` lists.
### 8.4 Start the visualization node

```bash
ros2 run restricted_zone_viz zone_viz
```

Expected log:

```
[INFO] [restricted_zone_visualizer]: restricted_zone_visualizer is running.
```

### 8.5 Publish a polygon (example: 1 m square at origin)

In a new terminal:

```bash
ros2 topic pub /restricted_zone/polygons geometry_msgs/PolygonStamped "
header:
  frame_id: map
polygon:
  points:
  - {x: 0.0, y: 0.0, z: 0.0}
  - {x: 1.0, y: 0.0, z: 0.0}
  - {x: 1.0, y: 1.0, z: 0.0}
  - {x: 0.0, y: 1.0, z: 0.0}
" -1
```

This continuously republishes, ensuring the layer receives data even after Nav2 restarts.

### 8.6 Open RViz (if not already running)

```bash
ros2 run rviz2 rviz2
```

Add displays:

* Map (`/map`)
* RobotModel
* Marker (`/restricted_zone/markers`)
* Global/Local Costmaps
* Path

You should see a red polygon and inflated/blocked cells in costmaps across that area.

### 8.7 Send a goal

Use **2D Nav Goal** in RViz.
If the goal lies across or inside the polygon, the planner should produce a path that detours around the restricted region.

---

## 9. Outcome

With the plugin enabled and polygons published in the `map` frame, Nav2 composes the restricted zone layer with other layers and produces paths that avoid these polygons. The visualization node provides clear operator feedback. Evidence files and bag recordings can be produced from the commands above for review and archival.

---

# Deliverable 3: Autonomous Patrol and Navigation

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
     
      
      source ~/geckon_ws/install/setup.bash
      export TURTLEBOT3_MODEL=burger
      ros2 launch turtlebot3_navigation2 navigation2.launch.py \
      use_sim_time:=True \
      map:=$HOME/geckon_ws/saved_maps/my_map.yaml

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
---
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
---
🎯 Expected Results

The robot performs autonomous waypoint patrol and pillar loop navigation.
RViz shows:
- Map with AMCL localization
- Global and local costmaps
- TF transforms
- Patrol path execution
- When replaying the bag file, the patrol loop is reproduced exactly as recorded.

---

# Deliverable 4: Trigger-Based Rerouting

This deliverable demonstrates **Trigger-Based Rerouting** using TurtleBot3 in Gazebo with the **Navigation2 (Nav2)** stack.  
During a patrol loop, the robot can accept an **external trigger** (via RViz “Publish Point” and a service call) to **interrupt its patrol**, navigate to the clicked location, and then **resume its regular patrol loop**.

---

## ✅ Features Implemented

- **Continuous patrol loop** using Navigation2 FollowWaypoints action  
- **Trigger-based rerouting** via RViz `/clicked_point` and `/patrol_manager/reroute_to_last_click` service  
- **Automatic resumption of patrol** after reroute completes  
- **Screen recording demo** (instead of bag file) uploaded to GitHub for evaluation  

---

## 🚀 Running Trigger-Based Rerouting

1. **Launch Gazebo simulation with TurtleBot3 world:**

               
               export TURTLEBOT3_MODEL=burger
               ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
2. **Launch Navigation2 with your saved map:**

               
               source ~/geckon_ws/install/setup.bash
               export TURTLEBOT3_MODEL=burger
               ros2 launch turtlebot3_navigation2 navigation2.launch.py \
               use_sim_time:=True \
               map:=$HOME/geckon_ws/saved_maps/my_map.yaml
3. **Start the waypoint follower (FollowWaypoints action server):**

               
               source ~/geckon_ws/install/setup.bash
               ros2 run nav2_waypoint_follower waypoint_follower
4. **Run Patrol Manager node (continuous looping patrol):**

               
               source ~/geckon_ws/install/setup.bash
               ros2 run waypoint_helper patrol_manager
      The robot will start looping around the waypoints defined in
      ~/geckon_ws/saved_maps/pillar_loop.yaml.

5. **Trigger rerouting:**
   - In RViz, select the Publish Point tool and click anywhere on the map.
   - Then call the reroute service:

               
               ros2 service call /patrol_manager/reroute_to_last_click std_srvs/srv/Trigger {}

     The robot will interrupt patrol → navigate to clicked point → resume patrol.

---

🎥 Demo Video

Since bag file recordings were not used for this deliverable, a screen recording was created and uploaded to this repository.
The video demonstrates:
- The robot patrolling continuously around a loop.
- An external trigger (clicked point in RViz) interrupting the patrol.
- The robot rerouting to the clicked point.
- Automatic resumption of the patrol loop after reaching the reroute destination.

This serves as direct visual evidence of Deliverable 4 functionality.

---
📝 Deliverable Explanation

Objective: Allow the patrol system to be interrupted by external events (e.g., operator command, alarm), handle the rerouting, and then gracefully resume normal operations.
Implementation:
- Patrol Manager node subscribes to /clicked_point.
- Provides service /patrol_manager/reroute_to_last_click.
- On service call, sends reroute goal to Nav2’s FollowWaypoints.
- After reaching the reroute destination, Patrol Manager resumes the waypoint patrol loop.
Outcome: System demonstrates adaptability and robustness — robot can both maintain routine patrols and handle unexpected commands without manual reset.
   


# Deliverable 5 – Reverse Motion Optimisation

---

## 🎯 Objective

The goal of this deliverable is to **enable reverse (backward) motion** in the Navigation2 (Nav2) local planner and demonstrate its advantage in narrow or constrained environments.  
When reverse motion is disabled, the robot must rotate 180° to reach goals behind it.  
With reverse motion optimisation, the robot can **drive backward directly** toward those targets, saving time and maintaining stability.

---

## ⚙️ Implementation Overview

Reverse motion capability was implemented using a dedicated node:  
**`reverse_motion_manager/reverse_toggle.py`**

This node dynamically enables or disables reverse movement in Nav2 by updating relevant planner and velocity smoother parameters through ROS 2 parameter services.

### Key Parameter Adjustments

| Component | Parameter | Forward-only | Reverse-enabled |
|------------|------------|---------------|-----------------|
| `controller_server` | `FollowPath.min_vel_x` | `0.0` | `-0.26` |
| `controller_server` | `FollowPath.vx_samples` | `20` | `20` |
| `controller_server` | `FollowPath.acc_lim_x` | `3.0` | `3.0` |
| `controller_server` | `FollowPath.decel_lim_x` | `-2.5` | `-2.5` |
| `velocity_smoother` | `min_velocity` | `[0.0, 0.0, -2.5]` | `[-0.5, 0.0, -2.5]` |

These parameters allow the DWB Local Planner and the Velocity Smoother to plan and execute trajectories with **negative linear velocities** (reverse motion).

---

## 🧩 System Nodes & Flow

**Core Nodes Involved**

- `turtlebot3_gazebo` – Simulated environment  
- `navigation2` – Full Nav2 stack (planner, controller, smoother)  
- `waypoint_follower` – FollowWaypoints action server  
- `waypoint_helper/patrol_manager` – Executes continuous patrol loops and handles rerouting  
- `reverse_motion_manager/reverse_toggle` – Enables/disables reverse dynamically

**Data Flow**

1. `patrol_manager` controls waypoints and patrol routes.  
2. Upon an external reroute command (`/patrol_manager/reroute_to_last_click`), the robot computes a new path.  
3. The `reverse_toggle` node can modify Nav2’s local planner parameters at runtime:  
   - **Disable reverse** → robot turns to face goal.  
   - **Enable reverse** → robot reverses directly to the target.  
4. After reaching the reroute goal, the patrol resumes normally.

---

## 🧠 Node Communication Diagram

            ```text
            +------------------+
            |  RViz            |
            |  (Publish Point) |
            +---------+--------+
                      |
                      v
               /clicked_point
                      |
                      v
            +-------------------------+
            |   waypoint_helper       |
            |   (Patrol Manager Node) |
            +-----------+-------------+
                        |
               /follow_waypoints action
                        |
                        v
            +------------------------+
            |  Nav2 Controller       |
            |  (DWB Local Planner)   |
            +-----------+------------+
                        |
                   /cmd_vel
                        |
                        v
            +--------------------+
            |  TurtleBot3 Base   |
            |  (Gazebo)          |
            +--------------------+
                        ^
                        |
              Reverse control via:
              /reverse_motion/enable
              /reverse_motion/disable
                        |
                        v
            +----------------------------+
            | reverse_motion_manager     |
            | (Reverse Toggle Node)      |
            +----------------------------+
---

### 🚀 Running the Simulation

1. Launch Gazebo

                            
                           export TURTLEBOT3_MODEL=burger
                           ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
2. Launch Navigation2 (with map and RViz)

                           
                           source ~/geckon_ws/install/setup.bash
                        export TURTLEBOT3_MODEL=burger
                        ros2 launch turtlebot3_navigation2 navigation2.launch.py \
                          use_sim_time:=True \
                          map:=$HOME/geckon_ws/saved_maps/my_map.yaml
3. Start Waypoint Follower

                           
                           source ~/geckon_ws/install/setup.bash
                        ros2 run nav2_waypoint_follower waypoint_follower
4. Start Patrol Manager

                           
                           source ~/geckon_ws/install/setup.bash
                        ros2 run waypoint_helper patrol_manager
5. Start Reverse Motion Manager

                           
                           source ~/geckon_ws/install/setup.bash
                        ros2 run reverse_motion_manager reverse_toggle

🔄 Test Procedure

Trial A – Forward-only (Reverse Disabled)

                        
                        ros2 service call /reverse_motion/disable std_srvs/srv/Trigger {}
a). In RViz, click a point behind the robot using the Publish Point tool.

b).  Trigger reroute:

                        
                        ros2 service call /patrol_manager/reroute_to_last_click std_srvs/srv/Trigger {}
c). The robot rotates to face the goal, moves forward to reach it, then resumes patrol.

---
Trial B – Reverse Enabled

                        
                        ros2 service call /reverse_motion/enable std_srvs/srv/Trigger {}
a). In RViz, click the same point behind the robot.

b). Trigger reroute again:

                        
                        ros2 service call /patrol_manager/reroute_to_last_click std_srvs/srv/Trigger {}
c). The robot drives backward directly toward the goal (negative linear.x velocity).
d). Upon reaching the point, it resumes the patrol loop.


* Observed Advantage
* Reverse motion reduced both path length and execution time, particularly in narrow corridors or when rerouting to points behind the robot.
