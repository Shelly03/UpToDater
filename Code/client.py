import socket
import psutil
import time
import snmpServer
import threading
import subprocess
from pyuac import main_requires_admin
import os


IP = "127.0.0.1"
MAIN_PORT = 65432
ALERT_PORT = 65431

CHECK_SECONDS = 5
THREAD_ALIVE = True

class client:
    def __init__(self):
        '''self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection_established = False
        while not connection_established:
            try:
                self.main_socket.connect((IP, MAIN_PORT))
                connection_established = True
            except Exception as e:
                print(e)

        self.info_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.info_socket.connect((IP, ALERT_PORT))
'''
        self.info_thread = threading.Thread(target=self.send_info)
        global THREAD_ALIVE
        THREAD_ALIVE = True
        #self.info_thread.start()
        
        self.open_dll_file()
                
        while True:
            print(snmpServer.get_gpu())
            time.sleep(0.5)

    def send_info(self):
        init_time = time.time()
        while THREAD_ALIVE:
            if time.time() - init_time > CHECK_SECONDS:
                check_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())).strip()
                cpu = str(snmpServer.get_cpu_usage()).strip() #TODO: fix cpu
                mem = str(snmpServer.get_virtual_mem()).strip()
                temp = str(0) 
                msg = str(', '.join([IP, cpu, temp, mem, check_time]))
                self.info_socket.send(msg.encode())

                init_time = time.time()
                
        
    @main_requires_admin
    def open_dll_file(self):
        # Specify the path to the EXE file
        exe_path = r"Code\sources\DLLS" #TODO: change directory so itll work on all comps
        os.chdir('\\'.join( [os.getcwd(), exe_path])) 
        # Open the EXE file with hidden window
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        proc = subprocess.Popen('OpenHardwareMonitor.exe', startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
        
        # Close the administrative Command Prompt window immediately
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(proc.pid)])
            # Exit the Python script to prevent further execution
        sys.exit()

    def disconnect(self):
        print("disconnect")
        self.main_socket.send("bye".encode())
        global THREAD_ALIVE
        THREAD_ALIVE = False
        self.main_socket.close()


c = client()
#c.disconnect()
