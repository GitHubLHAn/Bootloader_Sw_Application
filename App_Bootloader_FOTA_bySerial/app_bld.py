from communication import *
from readHex import *

import random

import os

import sys

from datetime import datetime

import winsound

def draw_progress_arrow(percent, total_slots=10):
    filled = int(percent / 100 * total_slots)

    if filled >= total_slots:
        bar = '-' * total_slots
    else:
        bar = '-' * filled + '>' + '_' * (total_slots - filled - 1)
        
    print(f"[{bar}] {percent:.0f}%")

SUCCESS		=	0x59
FAIL		=		0x4E

def crc8(data: bytes, length: int) -> int:
    """Tính CRC-8 cho mảng từ phần tử 0 đến length-2, bỏ qua phần tử cuối."""
    crc = 0
    for i in range(length - 1):  # Bỏ qua phần tử cuối cùng
        crc ^= data[i]
        for _ in range(8):
            crc = (crc << 1) ^ 0x07 if (crc & 0x80) else (crc << 1)
            crc &= 0xFF  # Giới hạn 8-bit
    return crc

def reverse_chunks_of_four(arr):
    if len(arr) % 4 != 0:
        raise ValueError("-> So luong phan tu trong chuoi data khong chia het cho 4")

    result = []
    for i in range(0, len(arr), 4):
        chunk = arr[i:i+4]
        result.extend(chunk[::-1])
    return result

# ------------------- Phan tich file hex ------------------------
print("\n>>> PHAN TICH FILE HEX\n")

# path_here = os.path.dirname(os.path.abspath(__file__))

path_here =  "E:\DEV_SPACE__\Bootloader_dev\Led_v3_mainCode\MDK-ARM\Led_board_v3"
path_firmware = path_here + "\Led_board_v3.hex"

print("-> Path FiwmWare: ", path_firmware)
    
lines_hexFile = parse_hex_file(path_firmware)

num_Line_hexFile = len(lines_hexFile)
print(f"-> Đã phân tích {num_Line_hexFile} dòng.")

size_off_dataHex = 0
list_data_flash = []
list_data_flash_reversed = []
cnt_line_data_flash = 0

for i, line in enumerate(lines_hexFile):
    if line['type'] == 4:
        phan_mo_rong_hex = line['data'][0]<<8 | line['data'][1]
        print(f"-> Phan mo rong: {hex(phan_mo_rong_hex)}")
                
        next_line = lines_hexFile[i+1]
        if next_line['type'] == 0:
            min_address = next_line["address"]
            max_address = next_line["address"]
        
    if line['type'] == 0:
        if line['address'] > max_address:
            max_address = line['address']            
        if line['address'] < min_address:
            min_address = line['address'] 
            
        size_off_dataHex += line['length'] 
        list_data_flash.append({"address" : line['address'], "data" : line['data']})
        list_data_flash_reversed.append({"address" : line['address'], "data" : line['data']})
    
    # print(f"[{i}] Addr: {line['address']:04X}, Type: {line['type']:02X}, Len: {line['length']}, Data: {line['data']}")

address_start_data = (phan_mo_rong_hex<<16) | min_address
address_end_data = (phan_mo_rong_hex<<16) | max_address

print("-> Dia chi bat dau ghi: ", hex(address_start_data))
print("-> Dia chi ket thuc: ", hex(address_end_data))

print("-> Kich thuoc chuong trinh firmware = ", str(size_off_dataHex), " bytes")

# for ino in range(0,len(list_data_flash)):
#     print(f"-> Dong {ino} - {list_data_flash[ino]} - Chua dao")
#     print(f"-> Dong {ino} - {list_data_flash_reversed[ino]} - Da dao")
winsound.Beep(3000, 500)    
    

# ------------------- Ping den MCU can FOTA ------------------------
ser = SerialHandler("COM3", 115200, 1)

ser.close()
ser.open()

mess_send = bytearray(30)
print("\n>>>>>>>> CONNECT DEVICE DESTINATION\n")
cnt = 10
while cnt > 0:
    
    mess_send[0] = 0x01
    mess_send[1] = 5
    mess_send[2] = 0x00
    mess_send[3] = random.randint(0, 200)
    mess_send[4] = crc8(mess_send, mess_send[1])

            
    ser.write(mess_send, mess_send[1])
    
    mess_receive = ser.read_message_idle(0.05, 1)
    
    if mess_receive[:mess_send[1]] == mess_send[:mess_send[1]]:
        print("-> Ket noi thanh cong den thiet bi can FOTA !")
        winsound.Beep(3000, 500)
        break
    else:
        print("-> Ket noi lai")
    cnt -= 1
    
    if cnt == 0:
        print("-> Ket noi that bai")
        ser.close()
        sys.exit()
    
    time.sleep(0.05)



# ------------------- Gui lenh erase flash ------------------------
print("\n>>> GUI LENH ERASE FLASH\n")
cnt = 3
while cnt > 0:
    
    mess_send[0] = 0x01
    mess_send[1] = 12
    mess_send[2] = 0x01
    mess_send[3] = (phan_mo_rong_hex >> 8) & 0xFF
    mess_send[4] = phan_mo_rong_hex & 0xFF
    mess_send[5] =  (address_start_data >> 8) & 0xFF
    mess_send[6] =  address_start_data & 0xFF
    mess_send[7] =  (address_end_data >> 8) & 0xFF
    mess_send[8] =  address_end_data & 0xFF
    mess_send[9] =  (size_off_dataHex >> 8) & 0xFF
    mess_send[10] = size_off_dataHex & 0xFF
    mess_send[11] = crc8(mess_send, mess_send[1])
            
    ser.write(mess_send, mess_send[1])
    
    mess_receive = ser.read_message_idle(0.05, 2)
    
    if mess_receive != []:
        if mess_receive[0] == mess_send[0] and mess_receive[2] == mess_send[2] and mess_receive[-1] == crc8(mess_receive, mess_receive[1]):
            if mess_receive[3] == SUCCESS: 
                print("-> Xoa flash thanh cong !")
                print("-> So luong pages/sectors da xoa: ", str(mess_receive[4]))
                winsound.Beep(3000, 500)
                break
            else:
                print("-> Xoa flash that bai, thu lai !")
        else:
            print("-> Ban tin phan hoi sai cau truc !")
    else:
        print("-> Gui lai lenh xoa")
        
    cnt -= 1
    if cnt == 0:
        print("-> Gui lenh xoa that bai")
        ser.close()
        sys.exit()
    
    time.sleep(0.5)




# ------------------- Gui lenh flash data ------------------------
print("\n>>>>>>>> GUI LENH FLASH DATA\n")

cnt_line_data = 0

start_flash = time.time()

cnt_error = 0

while cnt_line_data < len(list_data_flash_reversed):    
    mess_send[0] = 0x01
    mess_send[1] = len(list_data_flash_reversed[cnt_line_data]['data']) + 7
    mess_send[2] = 0x02
    
    mess_send[3] = (list_data_flash_reversed[cnt_line_data]['address'] >> 8) & 0xFF
    mess_send[4] = list_data_flash_reversed[cnt_line_data]['address'] & 0xFF
    mess_send[5] = len(list_data_flash_reversed[cnt_line_data]['data'])
    
    for j in range(0, len(list_data_flash_reversed[cnt_line_data]['data'])):
        mess_send[j+6] = list_data_flash_reversed[cnt_line_data]['data'][j]
        
    start_send = time.time()
    mess_send[mess_send[1]-1] = crc8(mess_send, mess_send[1])
    
    ser.write(mess_send, mess_send[1])
    
    # print_data_str(mess_send[:mess_send[1]])
    
    mess_receive = ser.read_message_idle(0.05, 2)
    
    # print("-> Time : ", str(time.time()-start_send))
    
    if mess_receive != []:
        if mess_receive[0] == mess_send[0] and mess_receive[2] == mess_send[2] and mess_receive[-1] == crc8(mess_receive, mess_receive[1]):
            if mess_receive[3] == SUCCESS: 
                print(f"-> Flash thanh cong {mess_receive[4]} bytes !")
                
                per = (cnt_line_data*100)/len(list_data_flash_reversed)
                draw_progress_arrow(per, 100)
                
                cnt_line_data += 1
            else:
                print("-> Flash du lieu that bai, thu lai !")
        else:
            print("-> Ban tin phan hoi sai cau truc !")
    else:
        # print("-> Gui lai du lieu Flash !")
        cnt_error += 1
        if cnt_error == 10:
            print("-> ERROR - Loi gui ban tin Flash qua 10 lan !")
            ser.close()
            sys.exit()
            
    
    time.sleep(0.001)
    
print("\n->   Flashing Success !\n")    

print("-> Flashing Interval time : ", str(time.time()-start_flash))
winsound.Beep(3000, 500)

# ------------------- Gui lenh flash data ------------------------
print("\n>>>>>>>> GUI LENH VERIFY DATA\n")





# ------------------- Gui lenh run Application ------------------------
print("\n>>>>>>>> GUI LENH  RESET VA RUN APPLICATION\n")

verion_code = 35
date_now = datetime.now()


cnt = 10
while cnt > 0:
    
    mess_send[0] = 0x01
    mess_send[1] = 13
    mess_send[2] = 0x04
    mess_send[3] = (phan_mo_rong_hex >> 8) & 0xFF
    mess_send[4] = phan_mo_rong_hex & 0xFF
    mess_send[5] =  (address_start_data >> 8) & 0xFF
    mess_send[6] =  address_start_data & 0xFF
    mess_send[7] =  verion_code
    mess_send[8] =  date_now.day
    mess_send[9] =  date_now.month
    mess_send[10] =  (date_now.year >> 8) & 0xFF
    mess_send[11] =  date_now.year & 0xFF
    mess_send[12] = crc8(mess_send, mess_send[1])
            
    ser.write(mess_send, mess_send[1])
    
    mess_receive = ser.read_message_idle(0.05, 2)
    
    if mess_receive != []:
        if mess_receive[0] == mess_send[0] and mess_receive[2] == mess_send[2] and mess_receive[-1] == crc8(mess_receive, mess_receive[1]):
            if mess_receive[3] == SUCCESS: 
                print("<===> Bootloading totally Finished !")
                winsound.Beep(3000, 1500)
                break
            else:
                print("-> Run application Fail !")
        else:
            print("-> Wrong received message !")
        
    cnt -= 1
    if cnt == 0:
        print("-> Run Application Fail !!!")
    
    time.sleep(0.1)

print("")
ser.close()