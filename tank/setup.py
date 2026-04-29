import os
from glob import glob
from setuptools import setup

package_name = 'tank'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        # Đánh dấu package với hệ thống ROS 2
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        # Cài đặt các thư mục chứa dữ liệu robot (CỰC KỲ QUAN TRỌNG)
        # Sử dụng glob('.../*') để lấy tất cả file bất kể viết hoa hay viết thường
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*')),
    ],
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
