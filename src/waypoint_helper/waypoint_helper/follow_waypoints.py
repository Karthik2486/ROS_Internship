#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped
import yaml
import os


class WaypointFollower(Node):
    def __init__(self):
        super().__init__('waypoint_follower_helper')

        # Action client for /follow_waypoints
        self._action_client = ActionClient(
            self, FollowWaypoints, '/follow_waypoints'
        )

    def load_waypoints(self, yaml_file):
        """Load waypoints from YAML file into PoseStamped list"""
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
        """Send waypoints to the /follow_waypoints action server"""
        self.get_logger().info("Waiting for /follow_waypoints server...")
        self._action_client.wait_for_server()

        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = waypoints

        self.get_logger().info(f"Sending {len(waypoints)} waypoints...")
        send_goal_future = self._action_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, send_goal_future)

        goal_handle = send_goal_future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Goal rejected!")
            return

        self.get_logger().info("Goal accepted. Waiting for result...")
        get_result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, get_result_future)

        result = get_result_future.result().result
        self.get_logger().info(f"Waypoint following finished with result: {result}")


def main(args=None):
    rclpy.init(args=args)
    node = WaypointFollower()

    # Declare parameter for YAML file
    yaml_file = node.declare_parameter(
        'waypoints_file',
        os.path.expanduser('~/geckon_ws/saved_maps/waypoints.yaml')
    ).value

    waypoints = node.load_waypoints(yaml_file)
    node.send_goal(waypoints)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

