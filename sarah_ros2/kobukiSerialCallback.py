import serial
import time
from sarah_ros2.OdomCalculate import OdomCalculate

class kobukiSerialCallback:
    def __init__(self, port):
        self.port = port
        self.baudrate = 115200
        self.serial_port = None
        self.WHEELBASE = 230 #mm
        self.TICK_TO_METER = 0.0000852920904977
        self.is_running = False
        self.timestamp = None
        self.bumper = None
        self.wheel_drop = None
        self.cliff = None
        self.left_encoder = None
        self.right_encoder = None
        self.left_pwm = None
        self.right_pwm = None
        self.button = None
        self.charge = None
        self.battery = None
        self.overcurent = None
        self.wheel_overcurrent = None
        self.odom = OdomCalculate()

    def connect(self):
        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )
            self.is_running = True
        except serial.SerialException as e:
            self.get_Logger().info(f"Erro ao iniciar comunicação na porta {self.port}: {e}")
    
    def disconnect(self):
            self.is_running = False
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()

    def sensor_read(self):
        if not self.serial_port or not self.serial_port.is_open:
            print('Porta serial fechada.')
            return
        count = 0
        while self.serial_port.in_waiting:
            if (self.serial_port.read(1) == b'\xAA'):
                if (self.serial_port.read(1) == b'\x55'):
                    length_bytes = self.serial_port.read(1)
                    if not length_bytes:
                        return False
                    length = ord(length_bytes)
                    package = self.serial_port.read(length) # lê o payload do pacote inteiro
                    if len(package) < length:
                        return False
                    sub_id = package[0]
                    sub_len = package[1]
                    if sub_id == 0x01 and sub_len == 0x0f:
                        self.timestamp = float(package[2]+(package[3]<<8))/1000
                        self.bumper = package[4]
                        self.wheel_drop = package[5]
                        self.cliff = package[6]
                        #self.wheel_overcurrent = package[7]
                        self.left_encoder = package[7] + package[8]*256
                        self.right_encoder = package[9]+ package[10]*256
                        self.left_pwm = package[11]
                        self.right_pwm = package[12]
                        self.button = package[13]
                        self.charge = package[14]
                        self.battery = float(package[15])/10
                        self.overcurent = package[16]
                        ds, dtheta = self.odom.update(self.left_encoder,
                                            self.right_encoder)
            count = count +1
            if count > 1000:
                self.get_logger().info("Falha de comunicação")
                return
    
    def _make_package(self, payload):
        length = len(payload)
        checksum = length
        for byte in payload:
            checksum ^= byte
        packet = (bytearray([0xAA, 0x55, length]) + payload + bytearray([checksum])) 
        return packet
    
    def send_vel(self, speed, radius):
        if not self.serial_port or not self.serial_port.is_open:
            print("Porta serial fechada.")
            return


        speed_b = speed.to_bytes(2, byteorder='little', signed=True)
        radius_b = radius.to_bytes(2, byteorder='little', signed=True)
        
        payload = bytearray([0x01, 0x04, speed_b[0] , speed_b[1], radius_b[0], radius_b[1]])
        packet = self._make_package(payload)
        try:
            self.serial_port.write(packet)
            self.serial_port.flush()  # Garante o envio imediato do buffer
            print(f"[SERIAL] Enviado: Speed = {speed} e raio = {radius}.")
        except Exception as e:
            print(f"Erro ao transmitir bytes pela serial: {e}")

def main():
    robot = kobukiSerialCallback(port = '/dev/ttyUSB0')
    robot.connect()
    try:
        while True:
            robot.sensor_read()
            print(f'Botton statur : {robot.button}')
            print(f'Bumper statur : {robot.bumper}')
            print(f'Battery voltage : {robot.battery}')
            time.sleep(1)
    except KeyboardInterrupt:
            # Permite parar o programa elegantemente pressionando Ctrl+C
            print("\nPrograma encerrado pelo usuário.")
    #robot.disconnect()

if __name__ == '__main__':
    main()