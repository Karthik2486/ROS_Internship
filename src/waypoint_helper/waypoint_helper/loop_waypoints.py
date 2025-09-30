#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped
import yaml
import os
import time


class LoopWaypointFollower(Node):
    def __init__(self):
        super().__init__('loop_waypoint_follower')
        self._action_client = ActionClient(self, FollowWaypoints, '/follow_waypoints')

    def load_waypoints(self, yaml_file):
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        waypoints = []
        for wp in data['waypoints']:
            pose = PoseStamped()
            pose.header.frame_id = "map"
            pose.pose.position.x = wp['position']['x']
            pose.pose.position.y = wp['position']['y']
            pose.pose.position.z = wp['position']['z']
            pose.pose.orientation.x = wp['orientation']['x']
            pose.pose.orientation.y = wp['orientation']['y']
            pose.pose.orientation.z = wp['orientation']['z']
            pose.pose.orientation.w = wp['orientation']['w']
            waypoints.append(pose)

        return waypoints

    def send_goal(self, waypoints):
        """Send one round of waypoints to the server and wait until done"""
        self._action_client.wait_for_server()
        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = waypoints

        self.get_logger().info(f"Sending {len(waypoints)} waypoints...")
        send_goal_future = self._action_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, send_goal_future)

        goal_handle = send_goal_future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Goal rejected!")
            return False

        get_result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, get_result_future)

        result = get_result_future.result().result
        self.get_logger().info(f"Round finished. Missed waypoints: {result.missed_waypoints}")
        return True


def main(args=None):
    rclpy.init(args=args)
    node = LoopWaypointFollower()

    yaml_file = os.path.expanduser('~/geckon_ws/saved_maps/waypoints.yaml')
    waypoints = node.load_waypoints(yaml_file)

    try:
        while rclpy.ok():
            node.send_goal(waypoints)
            node.get_logger().info("Loop complete, restarting in 2 seconds...")
            time.sleep(2.0)
    except KeyboardInterrupt:
        node.get_logger().info("Loop stopped by user.")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
