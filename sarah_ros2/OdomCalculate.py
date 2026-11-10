import  math


class OdomCalculate():
    def __init__(self):
        # =====================================================================
        # PARÂMETROS MECÂNICOS DO ROBÔ (Ajuste com os valores do seu hardware)
        # =====================================================================
        self.WHEEL_DIAMETER = 0.07       # Diâmetro da roda em metros (ex: 65mm)
        self.WHEEL_BASE = 0.230           # Distância entre as rodas em metros (ex: 20cm)
        self.TICKS_PER_REV = 2578.33          # Resolução do encoder (Ticks por volta completa)
        
        # Fator de conversão: metros percorridos por único tick
        self.METERS_PER_TICK = (math.pi * self.WHEEL_DIAMETER) / self.TICKS_PER_REV
        self.last_left = None
        self.last_right = None
        
        # Cumulative robot state
        self.x = 0.0      # meters
        self.y = 0.0      # meters
        self.theta = 0.0  # radians

    def update(self, current_left, current_right):
        """
        Updates the robot's displacement based on raw uint16 serial encoder inputs.
        :param current_left: Raw left encoder reading from serial packet (0-65535)
        :param current_right: Raw right encoder reading from serial packet (0-65535)
        :return: (delta_s, delta_theta) displacement and heading change for this step
        """
        # If it's the very first packet, initialize and return zero displacement
        if self.last_left is None or self.last_right is None:
            self.last_left = current_left
            self.last_right = current_right
            return 0.0, 0.0

        # 1. Calculate proper tick differences handling overflow
        delta_ticks_left = self._calculate_delta_ticks(current_left, self.last_left)
        delta_ticks_right = self._calculate_delta_ticks(current_right, self.last_right)

        # 2. Convert ticks to actual metric linear displacement per wheel
        d_left = delta_ticks_left * self.METERS_PER_TICK
        d_right = delta_ticks_right * self.METERS_PER_TICK

        # 3. Calculate total robot displacement (center point)
        delta_s = (d_left + d_right) / 2.0

        # 4. Calculate change in heading (rotation)
        delta_theta = (d_right - d_left) / self.WHEEL_BASE

        # 5. Dead reckoning update (Tracking absolute 2D Pose)
        self.theta += delta_theta
        # Keep theta bound between -pi and pi (optional but recommended)
        self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))
        
        self.x += delta_s * math.cos(self.theta)
        self.y += delta_s * math.sin(self.theta)

        # Update historical trackers for the next packet loop
        self.last_left = current_left
        self.last_right = current_right
        return delta_s, delta_theta

    def _calculate_delta_ticks(self, current, last):
        """Computes the signed difference between two 16-bit unsigned integers,
        handling the 0 -> 65535 and 65535 -> 0 overflow wrap-around."""
        # Standard delta calculation
        delta = current - last
        # Handle the 16-bit unsigned integer wrap-around bounds
        if delta > 32767:
            delta -= 65536
        elif delta < -32768:
            delta += 65536
        return delta