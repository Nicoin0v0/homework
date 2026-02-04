'''
实验名称：数据收发（从机）
版本：v1.0
作者：WalnutPi
说明：核桃派PicoW作为（从机），跟手机（主机）收发数据。
'''
    
import bluetooth,ble_simple_peripheral,time

#构建BLE对象
ble = bluetooth.BLE()

#构建从机对象,广播名称为WalnutPi，名称最多支持8个字符。
p = ble_simple_peripheral.BLESimplePeripheral(ble,name='WalnutPi')

#接收到主机发来的蓝牙数据处理函数
def on_rx(text):
    
    print("RX:",text) #打印接收到的数据,数据格式为字节数组。
    
    #回传数据给主机。
    p.send("I got: ") 
    p.send(text) 

#从机接收回调函数，收到数据会进入on_rx函数。
p.on_write(on_rx)
