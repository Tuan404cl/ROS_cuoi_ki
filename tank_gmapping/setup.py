import os
from glob import glob
from setuptools import setup

package_name = 'tank_gmapping'


def generate_data_files(share_path, dir_to_scan):
    data_files = []
    for path, _, files in os.walk(dir_to_scan):
        install_path = os.path.join(share_path, path)
        # Chỉ lấy những file thực sự tồn tại
        file_list = [os.path.join(path, f) for f in files]
        if file_list:
            data_files.append((install_path, file_list))
    return data_files

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        # Đánh dấu package với hệ thống ROS 2
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        # Cài đặt các thư mục chứa dữ liệu robot
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
        
        # NỐI DANH SÁCH MODELS VÀO ĐÂY BẰNG HÀM OS.WALK
    ] + generate_data_files('share/' + package_name, 'worlds/models'),
    
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Tuan',
    maintainer_email='tuan@uet.vnu.edu.vn',
    description='Robot Tank Description UET',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Thêm các file thực thi python ở đây sau này
        ],
    },
)
