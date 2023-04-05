import socket
import psutil
import time

IP = '127.0.0.1'
PORT = 65432  

class client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((IP, PORT))
        
    def disconnect(self):
        self.socket.sendall('bye'.encode())
        self.socket.close()
        
    def get_curr_cpu(self):
        psutil.cpu_percent()
        
c = client()
time.sleep(5)
c.disconnect()
print('disconnected')
