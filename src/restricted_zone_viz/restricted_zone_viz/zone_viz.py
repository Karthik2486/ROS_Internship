#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy
from geometry_msgs.msg import PolygonStamped, Point
from visualization_msgs.msg import Marker

class RestrictedZoneVisualizer(Node):
    """
    This node visualizes restricted zones published as PolygonStamped messages.
    It subscribes to /restricted_zone/polygons and publishes visual Marker lines
    to /restricted_zone/markers for easy viewing in RViz.
    """

    def __init__(self):
        super().__init__('restricted_zone_visualizer')

        # QoS ensures markers persist in RViz even if it starts later
        qos = QoSProfile(depth=1)
        qos.durability = QoSDurabilityPolicy.TRANSIENT_LOCAL
        qos.reliability = QoSReliabilityPolicy.RELIABLE

        # Subscribe to polygons from the restricted_zone_layer
        self.sub = self.create_subscription(
            PolygonStamped,
            '/restricted_zone/polygons',
            self.zone_cb,
            10
        )

        # Publish marker lines for RViz visualization
        self.pub = self.create_publisher(Marker, '/restricted_zone/markers', qos)

        self.scale = 0.06   # line width in meters
        self.color_rgba = (1.0, 0.1, 0.1, 1.0)  # red (RGBA)
        self.next_id = 0

        self.delete_all_markers()
        self.get_logger().info('restricted_zone_visualizer is running and listening on /restricted_zone/polygons')

    def delete_all_markers(self):
        """Remove old markers from RViz."""
        m = Marker()
        m.action = Marker.DELETEALL
        self.pub.publish(m)

    def zone_cb(self, msg: PolygonStamped):
        """Callback for drawing received restricted zone polygons."""
        m = Marker()
        m.header = msg.header
        m.ns = 'restricted_zones'
        m.id = self.next_id
        self.next_id += 1
        m.type = Marker.LINE_STRIP
        m.action = Marker.ADD
        m.scale.x = self.scale
        m.color.r, m.color.g, m.color.b, m.color.a = self.color_rgba

        # Convert points from the polygon to RViz marker format
        pts = []
        for p32 in msg.polygon.points:
            p = Point()
            p.x, p.y, p.z = float(p32.x), float(p32.y), float(p32.z)
            pts.append(p)

        # Close the polygon visually
        if pts:
            pts.append(pts[0])

        m.points = pts
        m.lifetime.sec = 0
        m.lifetime.nanosec = 0

        self.pub.publish(m)
        self.get_logger().info(f'Visualized polygon with {len(msg.polygon.points)} vertices (id={m.id})')

def main():
    rclpy.init()
    node = RestrictedZoneVisualizer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

