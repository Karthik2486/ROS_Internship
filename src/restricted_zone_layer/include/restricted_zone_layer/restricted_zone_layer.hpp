#ifndef RESTRICTED_ZONE_LAYER_HPP_
#define RESTRICTED_ZONE_LAYER_HPP_

#include <vector>
#include <string>
#include <mutex>
#include "rclcpp/rclcpp.hpp"
#include "nav2_costmap_2d/layer.hpp"
#include "nav2_costmap_2d/layered_costmap.hpp"
#include "geometry_msgs/msg/polygon_stamped.hpp"
#include "geometry_msgs/msg/point32.hpp"

namespace restricted_zone_layer_ns
{

class RestrictedZoneLayer : public nav2_costmap_2d::Layer
{
public:
  RestrictedZoneLayer();
  virtual void onInitialize() override;
  virtual void updateBounds(
    double robot_x, double robot_y, double robot_yaw,
    double* min_x, double* min_y, double* max_x, double* max_y) override;

  virtual void updateCosts(
    nav2_costmap_2d::Costmap2D & master_grid,
    int min_i, int min_j, int max_i, int max_j) override;

  virtual void reset() override;

  bool isClearable() { return false; }

private:
  void polygonCallback(const geometry_msgs::msg::PolygonStamped::SharedPtr msg);
  bool pointInPolygon(double x, double y,
                      const std::vector<geometry_msgs::msg::Point32> & poly);

  std::vector<geometry_msgs::msg::PolygonStamped> polygons_;
  rclcpp::Subscription<geometry_msgs::msg::PolygonStamped>::SharedPtr polygon_sub_;

  bool enabled_ = true;
  std::mutex data_mutex_;
};

}  // namespace restricted_zone_layer_ns

#endif  // RESTRICTED_ZONE_LAYER_HPP_

