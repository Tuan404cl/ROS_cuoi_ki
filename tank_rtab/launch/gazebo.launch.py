import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'tank_rtab'
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
        arguments=['-topic', 'robot_description', '-entity', 'tank_robot','-x', '0.0', '-y', '0.0', '-z', '0'],
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

    # 6. RTAB-Map (Phụ trách dựng 3D Point Cloud VÀ định vị TF)
    rtabmap_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('rtabmap_launch'), 'launch', 'rtabmap.launch.py')]),
        launch_arguments={
            'rtabmap_args': '--delete_db_on_start',
            'frame_id': 'base_link',
            'visual_odometry': 'false', # Đã có wheel odometry từ gazebo diff_drive
            'odom_topic': '/odom',
            'rgb_topic': '/camera/image_raw',
            'depth_topic': '/camera/depth/image_raw',
            'camera_info_topic': '/camera/camera_info',
            'approx_sync': 'true',
            'use_sim_time': 'true',
            'qos': '2',
            'rviz': 'false',
            'publish_tf_map': 'true' 
        }.items()
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
        TimerAction(period=2.0, actions=[rtabmap_node]),
        
        rviz_node
    ])
