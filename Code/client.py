import socket
import psutil
import time
import snmpServer
import threading

IP = '127.0.0.1'
PORT = 65432  

class client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((IP, PORT))
                
        self.alert_cpu_thread = threading.Thread(target=snmpServer.check_cpu, args=(self.socket, 0.7, 0.9, 5, ))
        self.alert_cpu_thread.start()
        
    def disconnect(self):
        print('disconnect')
        self.socket.send('bye'.encode())
        self.alert_cpu_thread.
        self.socket.close()
        

        
c = client()
time.sleep(1)
c.disconnect()

