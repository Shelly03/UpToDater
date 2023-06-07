from wakeonlan import send_magic_packet

def wake_device(mac, ip):
        send_magic_packet(mac,ip_address=ip)
        # Magic Packet Sent

        
wake_device('my_pc')
