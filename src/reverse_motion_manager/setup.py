from setuptools import find_packages, setup

package_name = 'reverse_motion_manager'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='karthik',
    maintainer_email='karthikjudo700@gmail.com',
    description='Toggle reverse motion for Nav2 at runtime',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'reverse_toggle = reverse_motion_manager.reverse_toggle:main',
        ],
    },
)

