from datetime import datetime
import time
import clr
import pandas as pd
import psutil
import threading
import sched
import wmi
import os
import pythoncom


def get_virtual_mem():
    # return virtual mem precentage
    return psutil.virtual_memory().percent

def get_drives_info():
    drives_info = {}
    
    # list of all drive letters
    drives = [disk.device for disk in psutil.disk_partitions()]
    
    # return info for each drive in dict
    for drive in drives:
        drives_info[drive] = psutil.disk_usage(drive)
    
    return drives_info

'''
bytes_sent: number of bytes sent
bytes_recv: number of bytes received
packets_sent: number of packets sent
packets_recv: number of packets received
errin: total number of errors while receiving
errout: total number of errors while sending
dropin: total number of incoming packets which were dropped
dropout: total number of outgoing packets which were dropped (always 0 on macOS and BSD)
'''
def get_network_info():
    return psutil.net_io_counters()

'''
fd: the socket file descriptor. If the connection refers to the current process this may be passed to socket.fromfd to obtain a usable socket object. On Windows and SunOS this is always set to -1.
family: the address family, either AF_INET, AF_INET6 or AF_UNIX.
type: the address type, either SOCK_STREAM, SOCK_DGRAM or SOCK_SEQPACKET.
laddr: the local address as a (ip, port) named tuple or a path in case of AF_UNIX sockets. For UNIX sockets see notes below.
raddr: the remote address as a (ip, port) named tuple or an absolute path in case of UNIX sockets. When the remote endpoint is not connected you’ll get an empty tuple (AF_INET*) or "" (AF_UNIX). For UNIX sockets see notes below.
status: represents the status of a TCP connection. The return value is one of the psutil.CONN_* constants (a string). For UDP and UNIX sockets this is always going to be psutil.CONN_NONE.
pid: the PID of the process which opened the socket, if retrievable, else None. On some platforms (e.g. Linux) the availability of this field changes depending on process privileges (root is needed).
'''
def get_connections_info():
    return psutil.net_connections()
    
'''
Return the addresses associated to each NIC (network interface card) installed on the system as a dictionary whose keys are the NIC names and value is a list of named tuples for each address assigned to the NIC. Each named tuple includes 5 fields:

family: the address family, either AF_INET or AF_INET6 or psutil.AF_LINK, which refers to a MAC address.
address: the primary NIC address (always set).
netmask: the netmask address (may be None).
broadcast: the broadcast address (may be None).
ptp: stands for “point to point”; it’s the destination address on a point to point interface (typically a VPN). broadcast and ptp are mutually exclusive. May be None.
'''
def get_network_interface_information():
    return psutil.net_if_addrs()

'''
percent: battery power left as a percentage.
secsleft: a rough approximation of how many seconds are left before the battery runs out of power. If the AC power cable is connected this is set to psutil.POWER_TIME_UNLIMITED. If it can’t be determined it is set to psutil.POWER_TIME_UNKNOWN.
power_plugged: True if the AC power cable is connected, False if not or None if it can’t be determined.

#TODO: check in laptop
'''
def get_battery_info():
    return psutil.sensors_battery()

'''
name: the name of the user.
terminal: the tty or pseudo-tty associated with the user, if any, else None.
host: the host name associated with the entry, if any.
started: the creation time as a floating point number expressed in seconds since the epoch.
pid: the PID of the login process (like sshd, tmux, gdm-session-worker, …). On Windows and OpenBSD this is always set to None.
'''
def get_users_info():
        return psutil.users()
        

def __get_info(s_type, s_name):
    pythoncom.CoInitialize()
    w = wmi.WMI(namespace="root\OpenHardwareMonitor")
    sensors = w.Sensor()
    for sensor in sensors:
        if sensor.SensorType==s_type:
            if sensor.Name == s_name:
                return sensor.Value
            
def get_cpu_temp():
    return __get_info('Temperature', 'CPU Package')

def get_gpu_temp():
    return __get_info('Temperature', 'GPU Core')

def get_cpu():
    return __get_info('Load', 'CPU Total')

def get_gpu():
    return __get_info('Load', 'GPU Core')

def get_processes_info():
    # the list the contain all process dictionaries
    processes = []
    for process in psutil.process_iter():
    # get all process info in one shot (more efficient, without making separate calls for each attribute)
        with process.oneshot():
            # get the process id
            pid = process.pid
            
            if pid == 0:
                # Swapper or sched process, useless to see 
                continue
            
            # get the name of the file executed
            name = process.name()
            
            # get the time the process was spawned
            try:
                create_time = datetime.fromtimestamp(process.create_time())
            except OSError:
                # system processes, using boot time instead
                create_time = datetime.fromtimestamp(psutil.boot_time())
            
            try:
                # get the number of CPU cores that can execute this process
                cores = len(process.cpu_affinity())
            except psutil.AccessDenied:
                cores = 0
            
            # get the CPU usage percentage
            cpu_usage = process.cpu_percent()
            
            # get the status of the process (running, idle, etc.)
            status = process.status()
            
            try:
                # get the process "niceness" (priority)
                nice = int(process.nice())
            except psutil.AccessDenied:
                nice = 0
                
            try:
                # get the memory usage in mbytes
                memory_usage = process.memory_full_info().uss / 1000000
            except psutil.AccessDenied:
                memory_usage = 0

            #number of threads the process has
            n_threads = process.num_threads()
            
            # get the username of user spawned the process
            try:
                username = process.username()
            except psutil.AccessDenied:
                username = "N/A"
            processes.append({
            'pid': pid, 'name': name, 'create_time': create_time,
            'cores': cores, 'cpu_usage': cpu_usage, 'status': status, 'nice': nice,
            'memory_usage': memory_usage, 'n_threads': n_threads, 'username': username,
            })
    return processes
    # convert to pandas dataframe
    df = pd.DataFrame(processes)
    # set the process id as index of a process
    df.set_index('pid', inplace=True)
    # convert to proper date format
    df['create_time'] = df['create_time'].apply(datetime.strftime, args=("%Y-%m-%d %H:%M:%S",))


