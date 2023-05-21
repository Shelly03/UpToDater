import socket
import psutil
import time
import snmpServer
import threading

IP = "127.0.0.1"
MAIN_PORT = 65432
ALERT_PORT = 65431

CHECK_SECONDS = 5
THREAD_ALIVE = True

class client:
    def __init__(self):
        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection_established = False
        while not connection_established:
            try:
                self.main_socket.connect((IP, MAIN_PORT))
                connection_established = True
            except Exception as e:
                print(e)

        self.info_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.info_socket.connect((IP, ALERT_PORT))

        self.info_thread = threading.Thread(target=self.send_info)
        global THREAD_ALIVE
        THREAD_ALIVE = True
        self.info_thread.start()

    def send_info(self):
        init_time = time.time()
        while THREAD_ALIVE:
            if time.time() - init_time > CHECK_SECONDS:
                check_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())).strip()
                cpu = str(snmpServer.get_cpu_usage()).strip() #TODO: fix cpu
                mem = str(snmpServer.get_virtual_mem()).strip()
                temp = str(0) #TODO: work on getting comp temp
                msg = str(', '.join([IP, cpu, temp, mem, check_time]))
                self.info_socket.send(msg.encode())

                init_time = time.time()


    def disconnect(self):
        print("disconnect")
        self.main_socket.send("bye".encode())
        global THREAD_ALIVE
        THREAD_ALIVE = False
        self.main_socket.close()


c = client()
time.sleep(10)
c.disconnect()
