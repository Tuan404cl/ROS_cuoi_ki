import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Khai báo biến để hứng tham số truyền vào từ file launch bên ngoài
    use_sim_time = LaunchConfiguration('use_sim_time')

    package_name = 'tank'
    pkg_share = get_package_share_directory(package_name)
    
    # SỬA Ở ĐÂY: Trỏ tới file xacro và dùng thư viện xacro để xử lý
    xacro_file = os.path.join(pkg_share, 'urdf', 'tank.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    robot_desc = robot_description_config.toxml()

    return LaunchDescription([
        # 2. Định nghĩa tham số use_sim_time
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'
        ),

        # 3. Truyền use_sim_time vào robot_state_publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc, 'use_sim_time': use_sim_time}]
        ),
        
        # 4. Truyền use_sim_time vào rviz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen'
        )
        
    ])
