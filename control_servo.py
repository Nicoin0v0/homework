import serial
import time
import random

#串口号
PORT = "COM3"
BAUDRATE = 115200

# 连接 PicoW
ser = serial.Serial(PORT, BAUDRATE, timeout=1)
print(f"已连接到 PicoW ({PORT})")

try:
    print("开始控制云台...")
    while True:
        # 随机生成角度
        horizontal = random.randint(-90, 90)   # 左右
        vertical = random.randint(-60, 30)     # 上下
        
        # 发送指令
        command = f"{horizontal},{vertical}\n"
        ser.write(command.encode('utf-8'))
        print(f"📡 发送: {command.strip()}")
        
        time.sleep(1)

except KeyboardInterrupt:
    ser.close()
    print("已断开连接")