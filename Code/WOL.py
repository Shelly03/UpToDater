'''from wakeonlan import send_magic_packet

def wake_device(mac, ip):
        send_magic_packet(mac,ip_address=ip)
        # Magic Packet Sent

wake_device('my_pc')'''


from scapy.all import *

def send_magic_packet(mac_address):
    # Create a WOL magic packet
    packet = Ether(dst='ff:ff:ff:ff:ff:ff') / \
             IP(dst='255.255.255.255') / \
             UDP(dport=9) / \
             Raw(load=(b'\xff' * 6 + (mac_address.replace(':', '') * 16).encode()))

    # Send the magic packet
    sendp(packet, verbose=0)

# Usage example
mac_address = '00:11:22:33:44:55'  # Replace with the MAC address of the target machine
send_magic_packet(mac_address)
