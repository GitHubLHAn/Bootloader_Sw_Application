import serial
import time

def print_data_str(data_s):
    print(' '.join(f'{b:02X}' for b in data_s))


class SerialHandler:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

    def open(self):
        try:
            self.ser = serial.Serial(port=self.port,
                                     baudrate=self.baudrate,
                                     timeout=self.timeout)
            print(f"[INFO] Opened port {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            print(f"[ERROR] Could not open port {self.port}: {e}")

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"[INFO] Closed port {self.port}")

    def write(self, data, length):
        if self.ser and self.ser.is_open:
            data_str = data[:length]
            if isinstance(data_str, str):
                data_str = data_str.encode()
            self.ser.write(data_str)
            print("-> SENT - ", end='') 
            print_data_str(data_str)
        else:
            print("[ERROR] Port not open")

    def receive(self, size=64):
        if self.ser and self.ser.is_open:
            data = self.ser.read(size)
            # print(f"[RECV] {data}")
            return data
        else:
            print("[ERROR] Port not open")
            return None
        
    def read_message_idle(self, idle_timeout=0.05, max_timeout=2):
        if self.ser and self.ser.is_open:
            message = b''
            start_time = time.time()
            
            at_least_1byte = False
            
            last_data_time = start_time         
            while True:
                if self.ser.in_waiting:
                    byte = self.ser.read(1)
                    message += byte
                    last_data_time = time.time()
                    at_least_1byte = True
                else:
                    if (time.time() - last_data_time) > idle_timeout:
                        # Không có dữ liệu mới trong khoảng thời gian idle_timeout
                        if at_least_1byte:
                            print("-> RECEIVED - ", end='') 
                            print_data_str(message)
                            break
                    if (time.time() - start_time) > max_timeout:
                        print("-> Rx time out")
                        message = []
                        return message
                time.sleep(0.001)
        else:
            message = []
            print("[ERROR] Port not open")
        return message