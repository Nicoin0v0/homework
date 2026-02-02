from machine import Pin, PWM
import bluetooth
import ble_simple_peripheral
import time
class Servo:
    def __init__(self, pin):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(50)
        self.current_angle = 0.0
        self.min_angle = -90
        self.max_angle = 90

    def _set_duty_by_angle(self, angle):
        angle = max(-90, min(90, angle))
        step1 = angle + 90          
        step2 = step1 * 2 / 180     
        step3 = step2 + 0.5        
        step4 = step3 / 20          
        duty = int(step4 * 1023)    
        self.pwm.duty(duty)
        self.current_angle = angle

    def set_angle_limits(self, min_angle, max_angle):
        self.min_angle = max(-90, min_angle)
        self.max_angle = min(90, max_angle)
        if self.min_angle > self.max_angle:
            self.min_angle, self.max_angle = self.max_angle, self.min_angle
        self.current_angle = max(self.min_angle, min(self.current_angle, self.max_angle))
        self._set_duty_by_angle(self.current_angle)

    def set_angle(self, angle):
        clamped_angle = max(self.min_angle, min(angle, self.max_angle))
        self._set_duty_by_angle(clamped_angle)

    def move_by(self, delta):
        target = self.current_angle + delta
        self.set_angle(target)

    def step(self, direction=1):
        self.move_by(direction)

    def move_at_speed(self, target_angle, speed_deg_per_sec):
        start = self.current_angle
        target = max(self.min_angle, min(target_angle, self.max_angle))
        if start == target:
            return
        total_deg = abs(target - start)
        total_time = total_deg / speed_deg_per_sec
        steps = int(total_deg) or 1 
        for i in range(steps + 1):
            ratio = i / steps
            angle = start + (target - start) * ratio
            self._set_duty_by_angle(angle)
            time.sleep(total_time / steps)

    def smooth_move_to(self, target_angle, duration=1.0):
        start = self.current_angle
        target = max(self.min_angle, min(target_angle, self.max_angle))
        if start == target:
            return
        steps = 50
        for i in range(steps + 1):
            ratio = i / steps
            angle = start + (target - start) * ratio
            self._set_duty_by_angle(angle)
            time.sleep(duration / steps)

    def smooth_move_by(self, delta, duration=1.0):
        self.smooth_move_to(self.current_angle + delta, duration)

    def get_angle(self):
        return self.current_angle

    def deinit(self):
        self.pwm.deinit()
pitch = Servo(pin=12)
yaw   = Servo(pin=11)
# 初始化位置
pitch.set_angle(0)
time.sleep(2)

yaw.set_angle(0)
time.sleep(1.5)

# === BLE 初始化 ===
ble = bluetooth.BLE()
p = ble_simple_peripheral.BLESimplePeripheral(ble, name='Walnut')

# === 蓝牙接收回调 ===
def on_rx(data):
    global pitch, yaw
    try:
        print("RX:", data)
        
        # 方向键 - 只响应"按下"事件
        if data == b'!B516':  # 上按下
            pitch.move_by(5)
            p.send(f"Pitch UP → {pitch.get_angle():.1f}°\n")
        elif data == b'!B615':  # 下按下
            pitch.move_by(-5)
            p.send(f"Pitch DOWN → {pitch.get_angle():.1f}°\n")
        elif data == b'!B714':  # 左按下
            yaw.move_by(-5)
            p.send(f"Yaw LEFT → {yaw.get_angle():.1f}°\n")
        elif data == b'!B813':  # 右按下
            yaw.move_by(5)
            p.send(f"Yaw RIGHT → {yaw.get_angle():.1f}°\n")
            
        # 数字键 - 直接响应
        elif data == b'!B11:':  # 数字1
            yaw.set_angle(-60)
            p.send(f"Yaw set to -60°\n")
        elif data == b'!B219':  # 数字2
            yaw.set_angle(-30)
            p.send(f"Yaw set to -30°\n")
        elif data == b'!B318':  # 数字3
            yaw.set_angle(0)
            p.send(f"Yaw set to 0°\n")
        elif data == b'!B417':  # 数字4
            yaw.set_angle(30)
            p.send(f"Yaw set to 30°\n")
            
    except Exception as e:
        p.send(f"Error: {e}\n")
p.on_write(on_rx)
print("等待手机连接...")
while True:
    time.sleep(0.1)