import sys
from machine import Pin, PWM
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

    def set_angle(self, angle):
        clamped_angle = max(self.min_angle, min(angle, self.max_angle))
        self._set_duty_by_angle(clamped_angle)

# 初始化舵机
pitch = Servo(pin=12)
yaw = Servo(pin=11)
pitch.set_angle(0)
yaw.set_angle(0)
time.sleep(1)

print("等待指令...")

while True:
    #修复后：直接读取，不使用 .any()
    line = sys.stdin.readline().strip()
    if line and ',' in line:
        try:
            h_str, v_str = line.split(',', 1)
            h = int(h_str)
            v = int(v_str)
            yaw.set_angle(h)
            pitch.set_angle(v)
            print(f"执行: Yaw={h}, Pitch={v}")
        except Exception as e:
            print("错误:", e)
    time.sleep(0.01)