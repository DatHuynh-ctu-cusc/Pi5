# bt_receiver.py
import serial
ser = serial.Serial('/dev/rfcomm0', 9600)
print("[Pi5] Đang nhận...")
while True:
    line = ser.readline().decode().strip()
    print("📩 Nhận:", line)
