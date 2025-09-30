from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Resolve the path to the params file inside this package's 'config' directory
    share_dir = get_package_share_directory('robot_config_pkg')
    params_file = os.path.join(share_dir, 'config', 'slam_params_sim.yaml')

    return LaunchDescription([
        Node(
            package='slam_toolbox',
            executable='sync_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[params_file]
        )
    ])
