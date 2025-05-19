from communication import *

import random

def crc8(data: bytes, length: int) -> int:
    """Tính CRC-8 cho mảng từ phần tử 0 đến length-2, bỏ qua phần tử cuối."""
    crc = 0
    for i in range(length - 1):  # Bỏ qua phần tử cuối cùng
        crc ^= data[i]
        for _ in range(8):
            crc = (crc << 1) ^ 0x07 if (crc & 0x80) else (crc << 1)
            crc &= 0xFF  # Giới hạn 8-bit
    return crc

ser = SerialHandler("COM3", 9600, 1)

ser.open()

mess_send = bytearray(30)

cnt = 10
while cnt > 0:
    
    mess_send[0] = 0x01
    mess_send[1] = 4
    mess_send[2] = 0x00
    mess_send[3] = crc8(mess_send, mess_send[1])
    
            
    ser.write(mess_send, mess_send[1])
    
    mess_receive = ser.read_message_idle(0.05, 2)
    
    # print_data_str(mess_receive)
    
    # print("Size rx = ", len(mess_receive))
    
    cnt -= 1
    time.sleep(0.05)



    
ser.close()