#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import sys, select, termios, tty

msg = """
========================================
   ĐIỀU KHIỂN KHỚP XE TANK BẰNG MŨI TÊN
========================================
Mũi tên LÊN    : Nâng cần (Prismatic +)
Mũi tên XUỐNG  : Hạ cần (Prismatic -)
Mũi tên TRÁI   : Xoay trái (Revolute +)
Mũi tên PHẢI   : Xoay phải (Revolute -)

CTRL-C để thoát
"""

class KeyboardJointController(Node):
    def __init__(self):
        super().__init__('keyboard_joint_controller')
        self.publisher_ = self.create_publisher(Float64MultiArray, '/joint_position_controller/commands', 10)
        self.prismatic_pos = 0.0
        self.revolt_pos = 0.0

    def publish_positions(self):
        # Khóa cứng giới hạn để tránh robot bị "gãy xương"
        self.prismatic_pos = max(min(self.prismatic_pos, 0.03), -0.03)
        self.revolt_pos = max(min(self.revolt_pos, 1.57), -1.57)

        msg_pub = Float64MultiArray()
        # Thứ tự mảng phải khớp chính xác với file controllers.yaml
        msg_pub.data = [self.prismatic_pos, self.revolt_pos]
        self.publisher_.publish(msg_pub)

def getKey(settings):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
        if key == '\x1b':  # Phát hiện ký tự bắt đầu của phím mũi tên
            key += sys.stdin.read(2)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardJointController()
    settings = termios.tcgetattr(sys.stdin)

    print(msg)
    try:
        while rclpy.ok():
            key = getKey(settings)
            if key == '\x1b[A':   # LÊN
                node.prismatic_pos += 0.002
                node.publish_positions()
            elif key == '\x1b[B': # XUỐNG
                node.prismatic_pos -= 0.002
                node.publish_positions()
            elif key == '\x1b[D': # TRÁI
                node.revolt_pos += 0.1
                node.publish_positions()
            elif key == '\x1b[C': # PHẢI
                node.revolt_pos -= 0.1
                node.publish_positions()
            elif key == '\x03':   # Ctrl-C
                break
    except Exception as e:
        print(e)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()