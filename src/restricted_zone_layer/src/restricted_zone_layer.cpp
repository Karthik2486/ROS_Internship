#include "restricted_zone_layer/restricted_zone_layer.hpp"
#include <pluginlib/class_list_macros.hpp>
#include <nav2_costmap_2d/costmap_math.hpp>
#include <geometry_msgs/msg/polygon_stamped.hpp>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>
#include <algorithm>

PLUGINLIB_EXPORT_CLASS(restricted_zone_layer_ns::RestrictedZoneLayer, nav2_costmap_2d::Layer)

namespace restricted_zone_layer_ns
{

RestrictedZoneLayer::RestrictedZoneLayer() {}

void RestrictedZoneLayer::onInitialize()
{
  auto node = node_.lock();  // ✅ lock the weak_ptr
  enabled_ = true;

  RCLCPP_INFO(node->get_logger(), "[RestrictedZoneLayer] Initialized and waiting for polygons...");

  polygon_sub_ = node->create_subscription<geometry_msgs::msg::PolygonStamped>(
    "/restricted_zone/polygons", rclcpp::QoS(10),
    std::bind(&RestrictedZoneLayer::polygonCallback, this, std::placeholders::_1));
}

void RestrictedZoneLayer::polygonCallback(const geometry_msgs::msg::PolygonStamped::SharedPtr msg)
{
  std::lock_guard<std::mutex> lock(data_mutex_);
  polygons_.push_back(*msg);

  auto node = node_.lock();
  RCLCPP_INFO(node->get_logger(),
              "[RestrictedZoneLayer] Received polygon with %zu points",
              msg->polygon.points.size());

  current_ = false;
}

void RestrictedZoneLayer::updateBounds(
  double /*robot_x*/, double /*robot_y*/, double /*robot_yaw*/,
  double* min_x, double* min_y, double* max_x, double* max_y)
{
  if (!enabled_) return;

  std::lock_guard<std::mutex> lock(data_mutex_);
  for (auto & poly : polygons_)
  {
    for (auto & p : poly.polygon.points)
    {
      // ✅ Explicitly cast float→double to avoid type mismatch
      *min_x = std::min(*min_x, static_cast<double>(p.x));
      *min_y = std::min(*min_y, static_cast<double>(p.y));
      *max_x = std::max(*max_x, static_cast<double>(p.x));
      *max_y = std::max(*max_y, static_cast<double>(p.y));
    }
  }
}

void RestrictedZoneLayer::updateCosts(
  nav2_costmap_2d::Costmap2D & master_grid,
  int min_i, int min_j, int max_i, int max_j)
{
  if (!enabled_) return;

  unsigned char lethal = nav2_costmap_2d::LETHAL_OBSTACLE;

  std::lock_guard<std::mutex> lock(data_mutex_);
  for (auto & poly : polygons_)
  {
    const auto & pts = poly.polygon.points;
    if (pts.size() < 3) continue;

    for (int j = min_j; j < max_j; j++)
    {
      for (int i = min_i; i < max_i; i++)
      {
        double wx, wy;
        master_grid.mapToWorld(i, j, wx, wy);

        if (pointInPolygon(wx, wy, pts))
        {
          master_grid.setCost(i, j, lethal);
        }
      }
    }
  }
}

bool RestrictedZoneLayer::pointInPolygon(double x, double y,
                                         const std::vector<geometry_msgs::msg::Point32> & poly)
{
  bool inside = false;
  size_t n = poly.size();
  for (size_t i = 0, j = n - 1; i < n; j = i++)
  {
    bool intersect = ((poly[i].y > y) != (poly[j].y > y)) &&
                     (x < (poly[j].x - poly[i].x) * (y - poly[i].y) /
                          (poly[j].y - poly[i].y) + poly[i].x);
    if (intersect)
      inside = !inside;
  }
  return inside;
}

void RestrictedZoneLayer::reset()
{
  std::lock_guard<std::mutex> lock(data_mutex_);
  polygons_.clear();
  auto node = node_.lock();
  RCLCPP_INFO(node->get_logger(), "[RestrictedZoneLayer] Zones cleared.");
}

}  // namespace restricted_zone_layer_ns

