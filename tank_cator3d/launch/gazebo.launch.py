import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'tank_cator3d'
    pkg_path = get_package_share_directory(package_name)
    
    # Map
    world_path = os.path.join(pkg_path, 'worlds', 'tank_world.world')
    
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
        '-x', '0', 
        '-y', '0', 
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
    
    # ---------- TÍCH HỢP CARTOGRAPHER 3D ----------
    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
        arguments=[
            '-configuration_directory', os.path.join(pkg_path, 'config'),
            '-configuration_basename', 'cartographer_3d.lua'
        ],
        remappings=[
            # Bắt buộc đổi thành points2_1 và points2_2
            ('points2_1', '/points2'),      # Nối luồng Lidar thứ 1
            ('points2_2', '/points2_2'),    # Nối luồng Lidar thứ 2
            
            ('imu', '/imu/data'),           # Nối luồng IMU dữ liệu
            ('odom', '/odom')               # Nối luồng Odom bánh xe
        ]
    )
    # Node Occupancy Grid (Xuất bản đồ 2D từ dữ liệu 3D cho RViz)
    cartographer_occupancy_grid_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='cartographer_occupancy_grid_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
        arguments=['-resolution', '0.05', '-publish_period_sec', '1.0']
    )




    rviz_config_file = os.path.join(pkg_path, 'config', 'tank_view.rviz')
        
    # 6. Khởi động RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': True}],
        output='screen'
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
        TimerAction(period=2.0, actions=[cartographer_node, cartographer_occupancy_grid_node]),
        
        rviz_node
    ])
