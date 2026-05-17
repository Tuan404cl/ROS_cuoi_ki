import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'tank_gmapping'
    pkg_path = get_package_share_directory(package_name)
    
    # Map
    world_path = os.path.join(pkg_path, 'worlds', 'bookstore.world')
    
    # 1. Xử lý file Xacro
    xacro_file = os.path.join(pkg_path, 'urdf', 'tank.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file).toxml()

    # 2. Node Robot State Publisher
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_config, 'use_sim_time': True}]
    )

    # 3. Mở Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
        launch_arguments={'world': world_path, 'use_sim_time': 'true'}.items()
    )

    # 4. Spawn Robot
    spawn_entity = Node(
    package='gazebo_ros',
    executable='spawn_entity.py',
    arguments=[
        '-topic', 'robot_description', 
        '-entity', 'tank_robot',
        '-x', '-2.3', 
        '-y', '6.2', 
        '-z', '0.05',  # Nên để cao hơn 0.0 một chút (5cm) để tránh robot bị kẹt vào sàn khi vừa spawn
        '-Y', '-1.72'  # Thêm tham số -Y (viết hoa) để định hướng robot quay đúng hướng
    ],
    output='screen'
)

    # ---------- PHẦN BỔ SUNG: KÍCH HOẠT CONTROLLERS ----------
    load_joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    load_joint_position_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_position_controller"],
    )
    # ---------------------------------------------------------
    
    rviz_config_file = os.path.join(pkg_path, 'config', 'tank_view.rviz')
    # 5. Khởi động RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # 6. Gmapping 2D
    gmapping_node = Node(
        package='slam_gmapping',
        executable='slam_gmapping_node',  # <--- CHỈ CẦN THÊM "_node" VÀO ĐÂY
        name='slam_gmapping',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'base_frame': 'base_link',
            'odom_frame': 'odom',
            'map_frame': 'map',
            'map_update_interval': 5.0,
            'maxUrange': 10.0,
            'maxRange': 12.0,
            'linearUpdate': 0.2,
            'angularUpdate': 0.2,
        }]
    )
    return LaunchDescription([
        rsp_node,
        gazebo,
        spawn_entity,
        
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn_entity,
                on_exit=[load_joint_state_broadcaster],
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=load_joint_state_broadcaster,
                on_exit=[load_joint_position_controller],
            )
        ),
        
        # Hẹn giờ chạy RTAB-Map (Đã gỡ SLAM Toolbox)
        TimerAction(period=2.0, actions=[gmapping_node]),
        
        rviz_node
    ])
