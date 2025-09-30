from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'robot_config_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        # Required for ROS 2 to find the package
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # Install ALL launch files (.py) in your launch/ folder
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),

        # Install ALL config files (.yaml) in your config/ folder
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),

        # (Optional) If you add RViz configs later:
        # (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='karthik',
    maintainer_email='karthik@todo.todo',
    description='Configs and launch files for EKF/SLAM',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # none
        ],
    },
)

