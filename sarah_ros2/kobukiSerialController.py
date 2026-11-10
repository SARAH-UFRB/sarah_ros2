import rclpy
import serial
import time
import threading

class kobukiSerialController:
    def __init__(self, port):
        self.port = port
        self.baudrate = 115200
        self.serial_port = None
        self.is_running = False
        self.timestamp = None
        self.bumper = None
        self.wheel_drop = None
        self.cliff = None
        self.left_encoder = None
        self.right_encode = None
        self.left_pwm = None
        self.right_pwm = None
        self.button = None
        self.charge = None
        self.battery = None
        self.overcurent = None

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
            print(f"Erro ao iniciar comunicação na porta {self.port}: {e}")
    
    def disconnect(self):
            self.is_running = False
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
    
    def start_sensor_update(self):
        self.thread_Sensor_Update = threading.Thread(
            target=self._sensor_read
        )
        self.thread_Sensor_Update.daemon = True
        self.thread_Sensor_Update.start()

    def _sensor_read(self):
        
        if not self.serial_port or not self.serial_port.is_open:
            print('Porta serial fechada.')
            return
        while self.is_running:
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
                        self.left_encoder = package[7]+package[8]<<8 
                        self.right_encode = package[9]+package[10]<<8
                        self.left_pwm = package[11]
                        self.right_pwm = package[12]
                        self.button = package[13]
                        self.charge = package[14]
                        self.battery = float(package[15])/10
                        self.overcurent = package[16]
                    package = self.serial_port.read(self.serial_port.in_waiting)


def main():
    robot = kobukiSerialController(port = '/dev/ttyUSB0')
    robot.connect()
    #sensor_update = 
    print('ola')
    robot.start_sensor_update()
    print('oi')
    try:
        while True:
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