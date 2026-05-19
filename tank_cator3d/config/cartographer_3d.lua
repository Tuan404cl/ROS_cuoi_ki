include "map_builder.lua"
include "trajectory_builder.lua"

options = {
  map_builder = MAP_BUILDER,
  trajectory_builder = TRAJECTORY_BUILDER,
  
  -- Các hệ tọa độ (Frames)
  map_frame = "map",
  tracking_frame = "imu_link",
  published_frame = "base_link",
  odom_frame = "odom",
  
  -- Cấu hình đầu vào
  provide_odom_frame = false, 
  publish_frame_projected_to_2d = false,
  
  use_odometry = true,
  use_nav_sat = false,
  use_landmarks = false,
  
  num_laser_scans = 0,
  num_multi_echo_laser_scans = 0,
  num_subdivisions_per_laser_scan = 1,
  num_point_clouds = 2
  
  lookup_transform_timeout_sec = 0.2,
  submap_publish_period_sec = 0.3,
  pose_publish_period_sec = 5e-3,
  trajectory_publish_period_sec = 30e-3,
}

MAP_BUILDER.use_trajectory_builder_3d = true
MAP_BUILDER.num_background_threads = 4

-- ĐÃ XÓA DÒNG GÂY LỖI: TRAJECTORY_BUILDER_3D.use_imu_data = true

-- Cấu hình Submap cho 3D
TRAJECTORY_BUILDER_3D.submaps.high_resolution = 0.10
TRAJECTORY_BUILDER_3D.submaps.high_resolution_max_range = 20.0
TRAJECTORY_BUILDER_3D.submaps.low_resolution = 0.45

return options