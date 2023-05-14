from wakeonlan import send_magic_packet

# TODO: make the packet with scapy
devices = {
'my_pc':{'mac':'bc:54:2f:f7:e7:e8','ip_address':'192.168.1.255'}
}
# TODO: check to see if works
def wake_device(device_name):
    if device_name in devices:
        mac,ip = devices[device_name].values()
        send_magic_packet(mac,ip_address=ip)
        print('Magic Packet Sent')
    else:
        print('Device Not Found')
        
wake_device('my_pc')
