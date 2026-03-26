import os
from glob import glob
from setuptools import setup, find_packages

package_name = 'auto_explore'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools', 'pyyaml'],
    zip_safe=True,
    maintainer='CDE2310 G10',
    maintainer_email='team@todo.todo',
    description='Independent mission control system for TurtleBot3 autonomous exploration',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mission_controller = auto_explore.mission_controller:main',
            'exploration_controller = auto_explore.exploration_controller:main',
            'pose_publisher = auto_explore.pose_publisher:main',
            'pose_subscriber = auto_explore.pose_subscriber:main',
        ],
    },
)
