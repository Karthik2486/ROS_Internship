#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped, PointStamped
from std_srvs.srv import Trigger
import yaml
import os


class PatrolManager(Node):
    def __init__(self):
        super().__init__('patrol_manager')

        # Default waypoint file
        default_file = os.path.expanduser('~/geckon_ws/saved_maps/pillar_loop.yaml')
        self.declare_parameter('waypoints_file', default_file)
        waypoints_file = self.get_parameter('waypoints_file').value

        # Load waypoints
        self._waypoints = self._load_waypoints(waypoints_file)

        # Action client
        self._action_client = ActionClient(self, FollowWaypoints, '/follow_waypoints')

        # Services
        self.create_service(Trigger, 'patrol_manager/reroute_to_last_click', self._on_reroute)
        self.create_service(Trigger, 'patrol_manager/resume_patrol', self._on_resume)
        self.create_service(Trigger, 'patrol_manager/stop_patrol', self._on_stop)

        # Subscribe to clicked_point (PointStamped from RViz)
        self._clicked_pose = None
        self.create_subscription(PointStamped, '/clicked_point', self._on_clicked_point, 10)

        # Control flags
        self._stopped = False
        self._rerouting = False

        self.get_logger().info(f"PatrolManager up. Waypoints file: {waypoints_file}")
        self.get_logger().info("Services: /patrol_manager/reroute_to_last_click, /patrol_manager/resume_patrol, /patrol_manager/stop_patrol")
        self.get_logger().info("Click a point in RViz (Publish Point tool) to set reroute target.")

        # Start patrol immediately
        self._send_patrol_goal()

    # ----------------------------
    # Load waypoints from YAML
    # ----------------------------
    def _load_waypoints(self, yaml_file):
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        waypoints = []
        for i, wp in enumerate(data['waypoints']):
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.pose.position.x = wp['position']['x']
            pose.pose.position.y = wp['position']['y']
            pose.pose.position.z = wp['position']['z']
            pose.pose.orientation.x = wp['orientation']['x']
            pose.pose.orientation.y = wp['orientation']['y']
            pose.pose.orientation.z = wp['orientation']['z']
            pose.pose.orientation.w = wp['orientation']['w']
            waypoints.append(pose)
            self.get_logger().info(f"Loaded WP{i}: ({pose.pose.position.x:.3f}, {pose.pose.position.y:.3f})")
        return waypoints

    # ----------------------------
    # Handle clicked point
    # ----------------------------
    def _on_clicked_point(self, msg: PointStamped):
        pose = PoseStamped()
        pose.header = msg.header
        pose.pose.position = msg.point
        pose.pose.orientation.w = 1.0
        self._clicked_pose = pose
        self.get_logger().info(f"Cached clicked pose: ({pose.pose.position.x:.2f}, {pose.pose.position.y:.2f})")

    # ----------------------------
    # Send patrol goal
    # ----------------------------
    def _send_patrol_goal(self):
        if self._stopped or self._rerouting:
            self.get_logger().warn("Patrol paused (stopped or rerouting), not sending patrol goal.")
            return
        if not self._action_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().error("FollowWaypoints action server not available.")
            return
        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = self._waypoints
        self.get_logger().info("Sending patrol goal...")
        send_future = self._action_client.send_goal_async(goal_msg)
        send_future.add_done_callback(self._patrol_goal_response)

    def _patrol_goal_response(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn("Patrol goal rejected.")
            return
        self.get_logger().info("Patrol goal accepted.")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._patrol_result)

    def _patrol_result(self, future):
        result = future.result().result
        self.get_logger().info(f"Patrol finished. Missed: {result.missed_waypoints}")
        if not self._stopped and not self._rerouting:
            self.get_logger().info("Restarting patrol cycle...")
            self._send_patrol_goal()

    # ----------------------------
    # Services
    # ----------------------------
    def _on_reroute(self, request, response):
        if self._clicked_pose is None:
            response.success = False
            response.message = "No clicked point cached yet."
            return response
        if not self._action_client.wait_for_server(timeout_sec=2.0):
            response.success = False
            response.message = "FollowWaypoints server not available."
            return response

        # Pause patrol
        self._rerouting = True
        self._stopped = True

        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = [self._clicked_pose]
        self.get_logger().info(f"Rerouting to clicked point: ({self._clicked_pose.pose.position.x:.2f}, {self._clicked_pose.pose.position.y:.2f})")
        send_future = self._action_client.send_goal_async(goal_msg)
        send_future.add_done_callback(self._reroute_goal_response)

        response.success = True
        response.message = "Reroute requested."
        return response

    def _reroute_goal_response(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn("Reroute goal rejected.")
            self._rerouting = False
            return
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._reroute_result)

    def _reroute_result(self, future):
        result = future.result().result
        self.get_logger().info(f"Reroute complete. Missed: {result.missed_waypoints}")
        # Resume patrol after reroute
        self._rerouting = False
        self._stopped = False
        self.get_logger().info("Resuming patrol after reroute...")
        self._send_patrol_goal()

    def _on_resume(self, request, response):
        self._stopped = False
        self.get_logger().info("Resume patrol requested.")
        self._send_patrol_goal()
        response.success = True
        response.message = "Resumed patrol."
        return response

    def _on_stop(self, request, response):
        self._stopped = True
        self.get_logger().info("Patrol stopped by service call.")
        response.success = True
        response.message = "Stopped patrol."
        return response


# ----------------------------
# Main
# ----------------------------
def main(args=None):
    rclpy.init(args=args)
    node = PatrolManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down PatrolManager.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

