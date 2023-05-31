import socket
import sys
import psutil
import time
import snmp_server
import threading
import subprocess
from pyuac import main_requires_admin
import pandas as pd
import os
from joblib import dump
from threading import Lock


IP = "127.0.0.1" # add file to store ip
MAIN_PORT = 65432
ALERT_PORT = 65431

CHECK_SECONDS = 30
THREAD_ALIVE = True
DISCONNECTING = False

FORBIDDEN_PROCESSES_NAMES = ["Notepad.exe"]


class client:
    def __init__(self):
        # create main socket
        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # client tries to connect the server
        connection_established = False
        while not connection_established:
            # incase the server is not up yet
            try:
                self.main_socket.connect((IP, MAIN_PORT))
                connection_established = True
            except Exception as e:
                # try again
                pass

        # create lock
        self.lock = Lock()
        
        # connect the socket responsinble for the info for the database
        self.info_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.info_socket.connect((IP, ALERT_PORT))

        # run a thread in the background to send the info
        self.info_thread = threading.Thread(target=self.send_info)
        global THREAD_ALIVE
        THREAD_ALIVE = True
        self.info_thread.start()

        # open the exe file so i can use the dll
        self.open_dll_exe()
        
        self.run()


    def send_info(self):
        init_time = time.time()
        while THREAD_ALIVE:
            self.lock.acquire()
            if time.time() - init_time > CHECK_SECONDS:
                check_time = str(
                    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                ).strip()
                cpu = str(snmp_server.get_cpu()).strip()  # TODO: fix cpu
                mem = str(snmp_server.get_virtual_mem()).strip()
                temp = str(snmp_server.get_cpu_temp())
                msg = str(", ".join([IP, cpu, temp, mem, check_time]))
                self.info_socket.send(msg.encode())

                self.check_for_forbidden_proccesses()

                init_time = time.time()
            self.lock.release()

    def check_for_forbidden_proccesses(self):
        processes = snmp_server.get_processes_info()
        for forbidden_process in FORBIDDEN_PROCESSES_NAMES:
            for process in processes:
                if process["name"] == forbidden_process:
                    msg = f"FORBDDEN PROCCESS RUNNING, {forbidden_process[0]}"
                    self.info_socket.send(msg.encode())
                    self.send_procmon(processes, self.info_socket)

    def send_procmon(self, processes, socket):
        data = str(processes)
        # Send the serialized data over the socket in packets
        packet_size = 4096
        total_size = len(data.encode())
        num_packets = total_size // packet_size + 1

        # Send the number of packets to expect
        socket.send(num_packets.to_bytes(4, byteorder="big"))

        # Send the serialized data in packets
        for i in range(num_packets):
            start = i * packet_size
            end = min(start + packet_size, total_size)
            packet = data[start:end]
            socket.send(packet.encode())

    @main_requires_admin
    def open_dll_exe(self):
        # Specify the path to the EXE file
        exe_path = r"sources\OpenHardwareMonitor\OpenHardwareMonitor.exe"
        exe_path = "\\".join([os.getcwd(), exe_path])
        
        # runs the exe as a daemon process
        subprocess.Popen([exe_path])
    
    def disconnect(self):
        # sends the server "bye" to notify disconnection
        self.lock.acquire()
        self.info_socket.send("bye".encode())
        self.lock.release()

        # notifies the other thread it has to finish
        global THREAD_ALIVE
        THREAD_ALIVE = False

        # close the main socket of the client
        self.main_socket.close()
        
    def run(self):
        while not DISCONNECTING:
            try:
                info = self.main_socket.recv(1064).decode()
                print(info)
                if info == 'hardware':
                    data = snmp_server.get_hardware_info()
                elif info == 'users':
                    data = {'name' : 'shelly', 'name' : 'guest'}
                elif info == 'net':
                    data = snmp_server.get_network_info()
                elif info == 'connections':
                    data = snmp_server.get_connections_info()
                else:
                    data = snmp_server.get_drives_info()
                print(data)
                data = str(data).encode()
                self.main_socket.send(data)
            except Exception as e:
                print(e)


c = client()
time.sleep(30)
c.disconnect()
