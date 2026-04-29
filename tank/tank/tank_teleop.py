import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class TankTeleop(Node):
    def __init__(self):
        super().__init__('tank_teleop')
        # Publish trực tiếp vận tốc vào controller của từng bánh
        self.publisher_ = self.create_publisher(Float64MultiArray, '/diff_cont/commands', 10)
        self.get_logger().info("Sử dụng AWSD để điều khiển bánh xe...")

    def send_velocity(self, left_vel, right_vel):
        msg = Float64MultiArray()
        msg.data = [left_vel, right_vel]
        self.publisher_.publish(msg)