from machine import UART, Pin, PWM
import time
uart = UART(1, 115200, rx=9, tx=10)
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
def uart_input(prompt=""):
    if prompt:
        uart.write(prompt.encode())
    while True:
        if uart.any():
            raw = uart.read()
            if raw:
                line = raw.decode('utf-8').strip()
                return line
        time.sleep(0.01)


pitch = Servo(pin=12)
yaw   = Servo(pin=11)
# 初始化位置
pitch.set_angle(0)
time.sleep(2)

yaw.set_angle(0)
time.sleep(1.5)
current_servo_name = "pitch"  # 默认控制 pitch 舵机
current_servo = pitch        # 默认舵机对象是 pitch
while True:
    # 菜单头部
    uart.write(("\n" + "="*50 + "\n").encode())
    uart.write(f"当前控制: {current_servo_name.upper()} 舵机\n".encode())
    uart.write("请选择要测试的功能：\n".encode())
    uart.write(f"1. 切换舵机 (当前: {current_servo_name})\n".encode())
    uart.write("2. 绝对角度控制\n".encode())
    uart.write("3. 相对角度控制\n".encode())
    uart.write("4. 按速度移动\n".encode())
    uart.write("5. 平滑移动（绝对）\n".encode())
    uart.write("6. 查询当前角度\n".encode())
    uart.write("0. 退出程序\n".encode())
    uart.write(("-"*50 + "\n").encode())
    
    choice = uart_input("请输入选项编号 (0-6): ").strip()
    
    try:
        if choice == "0":
            uart.write(" 程序结束，舵机保持当前位置。\n".encode())
            break

        elif choice == "1":
            if current_servo_name == "pitch":
                current_servo_name = "yaw"
                current_servo = yaw
            else:
                current_servo_name = "pitch"
                current_servo = pitch
            uart.write(f"已切换到 {current_servo_name.upper()} 舵机\n".encode())

        elif choice == "2":
            uart.write(f"\n🔹 测试：绝对角度控制 ({current_servo_name})\n".encode())
            angle_str = uart_input("请输入目标角度 (-90 ~ 90): ")
            angle = float(angle_str)
            current_servo.set_angle(angle)
            uart.write(f"已发送指令：转到 {angle}°\n".encode())

        elif choice == "3":
            uart.write(f"\n🔹 测试：相对角度控制 ({current_servo_name})\n".encode())
            delta_str = uart_input("请输入相对角度增量 (如 +20 或 -10): ")
            delta = float(delta_str)
            current_servo.move_by(delta)
            uart.write(f"已相对移动 {delta}°\n".encode())

        elif choice == "4":
            uart.write(f"\n🔹 测试：按速度移动 ({current_servo_name})\n".encode())
            target_str = uart_input("请输入目标角度 (-90 ~ 90): ")
            speed_str = uart_input("请输入速度 (度/秒，如 30): ")
            target = float(target_str)
            speed = float(speed_str)
            uart.write(f"正在以 {speed}°/秒 的速度移动到 {target}°...\n".encode())
            current_servo.move_at_speed(target, speed)
            uart.write(" 移动完成\n".encode())

        elif choice == "5":
            uart.write(f"\n🔹 测试：平滑移动 ({current_servo_name})\n".encode())
            target_str = uart_input("请输入目标角度 (-90 ~ 90): ")
            duration_str = uart_input("请输入持续时间 (秒，如 2.0): ")
            target = float(target_str)
            duration = float(duration_str)
            uart.write(f"正在 {duration} 秒内平滑移动到 {target}°...\n".encode())
            current_servo.smooth_move_to(target, duration)
            uart.write("平滑移动完成\n".encode())

        elif choice == "6":
            angle = current_servo.get_angle() 
            uart.write(f"当前 {current_servo_name} 舵机角度: {angle:.1f}°\n".encode())

        else:
            uart.write("无效选项，请输入 0-6 之间的数字\n".encode())

        # 每次操作后暂停一下
        if choice in ["2", "3", "4", "5"]:
            time.sleep(0.5)

    except ValueError:
        uart.write(" 输入格式错误，请输入数字！\n".encode())
    except KeyboardInterrupt:
        uart.write("\n用户中断\n".encode())
        break
    except Exception as e:
        uart.write(f"发生错误: {e}\n".encode())