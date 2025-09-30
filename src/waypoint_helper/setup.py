from setuptools import find_packages, setup

package_name = 'waypoint_helper'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='karthik',
    maintainer_email='karthik@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        	'follow_waypoints = waypoint_helper.follow_waypoints:main',
        	'loop_waypoints = waypoint_helper.loop_waypoints:main',
        	'patrol_manager = waypoint_helper.patrol_manager:main',

        ],
    },
)
