import socket
import psutil
import time
import snmpServer
import threading

IP = "127.0.0.1"
MAIN_PORT = 65432
ALERT_PORT = 65431

THRED_ALIVE = True

CHECK_SECONDS = 5

MAX_CPU = 0.9
WARN_CPU = 0.7


class client:
    def __init__(self):
        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection_established = False
        while not connection_established:
            try:
                self.main_socket.connect((IP, MAIN_PORT))
                connection_established = True
            except:
                print("here")

        self.alert_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.alert_socket.connect((IP, ALERT_PORT))

        THRED_ALIVE = True
        self.alert_cpu_thread = threading.Thread(target=self.check_alerts)
        self.alert_cpu_thread.start()
        print("thread up")

    def check_alerts(self):
        init_time = time.time()
        while THRED_ALIVE:
            if time.time() - init_time > CHECK_SECONDS:
                init_time = time.time()
                self.check_cpu()
                # TODO: add mpre checks
        return

    def check_cpu(self):
        cpu = snmpServer.get_cpu_usage()
        print(cpu)
        if cpu > MAX_CPU:
            self.alert_socket.send("cpu:alert".encode())
        elif cpu > WARN_CPU:
            self.alert_socket.send("cpu:warning".encode())
        else:
            self.alert_socket.send("cpu:good".encode())

    def disconnect(self):
        print("disconnect")
        self.main_socket.send("bye".encode())
        THRED_ALIVE = False
        self.main_socket.close()


c = client()
time.sleep(30)
c.disconnect()
