# my_std_msgs/
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist, TransformStamped, Quaternion
from tf2_ros import TransformBroadcaster
from sarah_ros2.kobukiSerialCallback import kobukiSerialCallback
import math


class Kobuki_robot(Node):

    def __init__(self):
        super().__init__('kobuki_robot')
        # iniciando comunicacao
        self.robot = kobukiSerialCallback(port = '/dev/kobuki')
        self.robot.connect()
        # iniciando topico de leitura dos comandos de velocidade
        self.cmd_vel_subscriber = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10) 
        # iniciando topicos de postagem dos sensores
        self.tf_broadcaster = TransformBroadcaster(self)
        self.Bumper_publisher_ = self.create_publisher(String, '/mobile_base/events/bumper', 10)
        self.Button_publisher_ = self.create_publisher(String, '/mobile_base/events/button', 10)
        self.odom_publisher_ = self.create_publisher(Odometry, '/odom', 10)
        timer_period = 1  # seconds
        self.timer = self.create_timer(timer_period, self.sensorPublisher)
        self.active_bumper = None


    def cmd_vel_callback(self, msg):
        WHEELBASE= 0.23 # distancia entre rodas 0.230 m
        vel_linear = msg.linear.x*1000          # velocidade em mm/s
        vel_angular = msg.angular.z             # velocidade angular rad/s
        speed = 0.0
        radius = 0.0
        # Caso 1: Rotação pura
        if abs(vel_linear) < 1e-4 and abs(vel_angular)> 1e-4:
            speed = vel_angular*self.robot.WHEELBASE/2.0
            radius = 1  # 1mm significa rotação no eixo
        # Caso 2: Translação pura
        elif abs(vel_angular) < 1e-4:
            speed = int(vel_linear)
            radius = 0  # 0mm significa movimento em linha reta
        # Caso 3: Movimento combinado
        elif abs(vel_linear) >= 1e-4 and abs(vel_angular) >= 1e-4:
            radius = vel_linear / vel_angular
            # Limite de raio
            radius = max(-32768, min(32767, speed))
            # formula de conversão de velocidade
            if radius > 1:
                speed = vel_linear * (radius + self.robot.WHEELBASE / 2.0)/radius
            if radius < -1:
                speed = vel_linear * (radius - self.robot.WHEELBASE/ 2.0)/radius
            else:
                speed = vel_linear
        else:
            speed = 0
            radius = 0
        speed = max(-200, min(200, speed))
        self.get_logger().info(f'vel. linear: {msg.linear.x}')
        self.get_logger().info(f'vel. angular: {msg.angular.z}')
        #print(f'speed = {speed}, radius={radius}')
        self.robot.send_vel(speed=int(speed), radius=int(radius))

    def sensorPublisher(self):
        self.robot.sensor_read()
        msg = String()
        msg.data = str(self.robot.bumper)
        self.Bumper_publisher_.publish(msg)
        msg.data = str(self.robot.button)
        self.Button_publisher_.publish(msg)
        #msg.data = str(f"x:{self.robot.right_encoder} - y: {self.robot.left_encoder} - theta: {self.robot.odom.theta}")
        #msg.data = str(f"x:{self.robot.odom.x} - y: {self.robot.odom.y} - theta: {self.robot.odom.theta}")
        self._publish_odom(self.robot.odom.x, self.robot.odom.y, self.robot.odom.theta)

    def _euler_to_quaternion(self, roll, pitch, yaw):
        """Helper function to convert Euler angles to a geometry_msgs Quaternion."""
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        q = Quaternion()
        q.w = cr * cp * cy + sr * sp * sy
        q.x = sr * cp * cy - cr * sp * sy
        q.y = cr * sp * cy + sr * cp * sy
        q.z = cr * cp * sy - sr * sp * cy
        return q

    def _publish_odom(self, x, y, theta):

        current_time = self.get_clock().now().to_msg()
        # converte theta (yaw) para quarternio
        odom_quat = self._euler_to_quaternion(0.0, 0.0, theta)
        # divulgando transfomada odom->base_link
        t = TransformStamped()
        t.header.stamp = current_time
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'

        t.transform.translation.x = x
        t.transform.translation.y = y
        t.transform.translation.z = 0.0
        t.transform.rotation = odom_quat

        self.tf_broadcaster.sendTransform(t)
        # preparando mensagem de odometria
        odom = Odometry()
        odom.header.stamp = current_time
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'
        # definindo posição
        odom.pose.pose.position.x = x
        odom.pose.pose.position.y = y
        odom.pose.pose.position.z = 0.0
        odom.pose.pose.orientation = odom_quat
        # definindo velocidades (opcional)
        odom.twist.twist.linear.x = 0.0 #vx
        odom.twist.twist.linear.y = 0.0 #vy
        odom.twist.twist.angular.z = 0.0 #self.vth
        # publicando a mensagem
        self.odom_publisher_.publish(odom)

def main(args=None):

    rclpy.init(args=args)
    minimal_publisher = Kobuki_robot()
    
    # Spin the node so the timer callbacks are processed
    rclpy.spin(minimal_publisher)

    # Clean up and destroy the node explicitly
    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
