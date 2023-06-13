import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import smtplib
import ssl
import traceback
import pythoncom 
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
from threading import Lock


IP = "10.30.57.8" # add file to store ip
MAIN_PORT = 65432
ALERT_PORT = 65431

TIME_BETWEEN_CHECKS = 30
TIME_BETWEEN_EMAILS = 1800
TIME_TRACKER = {'cpu':time.time(), 'temp':time.time(), 'mem':time.time(), 'forbidden_processes':time.time()}

THREAD_ALIVE = True
DISCONNECTING = False

NV_PASSWORD =  'wmwhkhwgbbklsevo'
NV_EMAIL = 'netvigilantnotifier@gmail.com'


class client:
    def __init__(self):
        # create lock
        self.lock = Lock()
        
        # open the exe file so i can use the dll
        self.open_dll_exe()
        
        self.connect_to_server()


    def connect_to_server(self):
        print('connect to server')
        # create main socket
        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.info_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        init_time = time.time()
        self.admin_settings = self.get_settings_file()
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
            finally:
                if time.time() - init_time > TIME_BETWEEN_CHECKS and self.admin_settings != '':
                    print('started check')
                    self.check_performance()
                    init_time = time.time()
        
        # connect the socket responsinble for the info for the database
        self.info_socket.connect((IP, ALERT_PORT))
        print('connected')

        # get admin settings
        self.admin_settings = json.loads(self.main_socket.recv(4096).decode())
        self.write_settings_file(self.admin_settings)


        # run a thread in the background to send the info
        self.info_thread = threading.Thread(target=self.send_info)
        global THREAD_ALIVE
        THREAD_ALIVE = True
        self.info_thread.start()

        self.run()


    def send_info(self):
        init_time = time.time()
        try:
            while THREAD_ALIVE:
                self.lock.acquire()
                if time.time() - init_time > TIME_BETWEEN_CHECKS:
                    check_time = str(
                        time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                    ).strip()
                    cpu = str(snmp_server.get_cpu()).strip()  # TODO: fix cpu
                    mem = str(snmp_server.get_virtual_mem()).strip()
                    temp = str(snmp_server.get_cpu_temp())
                    msg = str(", ".join([IP, cpu, temp, mem, check_time]))
                    self.info_socket.send(msg.encode())

                    self.check_performance()

                    init_time = time.time()
                self.lock.release()
        except Exception as e:
            print(e)
        finally:
            self.info_socket.close()
            self.connect_to_server()

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
        try:
            while not DISCONNECTING:
                info = self.main_socket.recv(4096).decode()
                if info == 'hardware':
                    data = snmp_server.get_hardware_info()
                elif info == 'users':
                    data =snmp_server.get_users_info()
                elif info == 'net':
                    data = snmp_server.get_network_info()
                elif info == 'connections':
                    data = snmp_server.get_connections_info()
                elif info == 'running processes':
                    data = snmp_server.get_processes_info()
                else:
                    data = snmp_server.get_drives_info()
                data = json.dumps(data).encode()
                
                # Calculate the number of packets required
                total_packets = (len(data) // 1064) + 1

                # Send the total number of packets
                self.main_socket.send(str(total_packets).zfill(4).encode())

                # Send the data packets
                for packet_number in range(total_packets):
                    start_index = packet_number * 1064
                    end_index = (packet_number + 1) * 1064
                    packet_data = data[start_index:end_index]
                    self.main_socket.send(packet_data)

        except Exception as e:
            global THREAD_ALIVE
            THREAD_ALIVE = False
            self.main_socket.close()
            print('disconnect')

    def write_settings_file(self, settings_data):
        with open('Admin_settings.txt', 'w') as file:
            file.write("max_cpu:{}\n".format(settings_data["max_cpu"]))
            file.write("max_cpu_temp:{}\n".format(settings_data["max_cpu_temp"]))
            file.write("max_mem:{}\n".format(settings_data["max_mem"]))
            
            file.write("\nforbidden_processes:\n")
            for process in settings_data["forbidden_processes"]:
                file.write('{}\n'.format(process))
            
            file.write("\nemail:{}\n".format(settings_data["email"]))
            
    def get_settings_file(self):
        settings_data = {}

        try:
            with open('Admin_settings.txt', 'r') as file:
                lines = file.readlines()

                for line in lines:
                    line = line.strip()

                    if line.startswith("max_cpu:"):
                        settings_data["max_cpu"] = int(line.split(":")[1])
                    elif line.startswith("max_cpu_temp:"):
                        settings_data["max_cpu_temp"] = int(line.split(":")[1])
                    elif line.startswith("max_mem:"):
                        settings_data["max_mem"] = int(line.split(":")[1])
                    elif line == "forbidden_processes:":
                        settings_data["forbidden_processes"] = []
                    elif line.endswith('.exe'):
                        settings_data["forbidden_processes"].append(line.strip('"'))
                    elif line.startswith("email:"):
                        settings_data["email"] = line.split(":")[1].strip()
        except FileNotFoundError:
            return ''

        return settings_data

    def check_performance(self):
        cpu = snmp_server.get_cpu()
        temp = snmp_server.get_cpu_temp()
        mem = snmp_server.get_virtual_mem()
        processes = snmp_server.get_processes_info()
        
        msg = ''
        if cpu > self.admin_settings['max_cpu'] and time.time() - TIME_TRACKER['cpu'] > TIME_BETWEEN_EMAILS:
            msg += "This computer's cpu usage is above the limit, it is {}%\n".format(cpu)
            
        if temp > self.admin_settings['max_cpu_temp'] and time.time() - TIME_TRACKER['temp'] > TIME_BETWEEN_EMAILS:
            msg += "This computer's cpu temprature usage is above the limit, it is {}\n".format(temp)
            
        if mem > self.admin_settings['max_mem'] and time.time() - TIME_TRACKER['mem'] > TIME_BETWEEN_EMAILS:
            msg += "This computer's virtual memory is above the limit, it is {}%\n".format(mem)
            
        forbidden_processes_detected = set()  # Track detected forbidden processes
        if time.time() - TIME_TRACKER['forbidden_processes'] > TIME_BETWEEN_EMAILS:
            for forbidden_process in self.admin_settings['forbidden_processes']:
                for process in processes:
                    if process["name"] == forbidden_process:
                        if forbidden_process not in forbidden_processes_detected:
                            msg += "This computer is running a process you defined as forbidden - {}\n".format(process["name"])
                            forbidden_processes_detected.add(forbidden_process)
                            
        if msg != '':
            if len(forbidden_processes_detected)>0:
                df = pd.DataFrame(processes)
                file_name = f"processes of {socket.gethostbyname(socket.gethostname())}.xlsx"
                df.to_excel(file_name, index=False)
                self.send_email(msg, file_name)
                os.remove(file_name)
            else:
                self.send_email(msg)

    def send_email(self, message, attachment_path=None):
        print('preparing email')
        message = f'Hi, this is a notification regardint the computer {socket.gethostbyname(socket.gethostname())} in your system\n' + message
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"

        # Create the email message
        msg = MIMEMultipart()
        msg["From"] = NV_EMAIL
        msg["To"] = self.admin_settings['email']
        msg["Subject"] = 'NETVIGILANT Notification'

        # Attach the message content
        msg.attach(MIMEText(message, "plain"))

        # Attach the file if provided
        if attachment_path:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {attachment_path}",
            )
            msg.attach(part)

        # Connect to the SMTP server and send the email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(NV_EMAIL, NV_PASSWORD)
            server.sendmail(NV_EMAIL, self.admin_settings['email'], msg.as_string())
        print('sent')

c = client()

