import datetime
import time
import psutil
import threading
import sched


def check_cpu(socket, warning_cpu, alert_cpu, cpu_time_check):
    init_time = time.time()
    while(True):
        if(time.time() - init_time > cpu_time_check):
            init_time = time.time()
            cpu = get_cpu_usage()
            if(cpu > alert_cpu):
                socket.send('alert')
            elif(cpu > warning_cpu):
                socket.send('warning')

def get_cpu_usage():
    # return cpu precentage times the number of physical cores
    return psutil.cpu_percent(0.5) / psutil.cpu_count()

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
        


