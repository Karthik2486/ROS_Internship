from setuptools import setup

package_name = 'restricted_zone_viz'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='karthik',
    maintainer_email='karthik@example.com',
    description='Visualizes /restricted_zones polygons in RViz',
    license='Apache License 2.0',
    entry_points={
        'console_scripts': [
            'zone_viz = restricted_zone_viz.zone_viz:main',
        ],
    },
)

