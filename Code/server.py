import uuid
from joblib import load
import socket
import threading
import sqlite3
import os
from threading import Lock
import subprocess
from database import database


MAIN_PORT = 65432
ALERT_PORT = 65431

# dict to save the ip and socket of computers
COMPUTERS = {}

class server:
    
    def __init__(self):

        # start main socket
        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_socket.bind(("0.0.0.0", MAIN_PORT))
        self.main_socket.listen(5)
        print("> MAIN SERVER ON")

        # start the socket for the info and the alerts
        self.alert_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.alert_socket.bind(("0.0.0.0", ALERT_PORT))
        self.alert_socket.listen(5)
        print("> INFO SERVER ON")

        # create lock instance
        self.lock = Lock()

        # create DB handler instance
        self.database = database()
        


    def get_comp_info(self, client_conn, client_address): 
        self.update_database_connection(client_address, 'on')
        try:
            while True:

                try:
                    data = client_conn.recv(1024).decode()
                    
                    if data == 'bye':
                        break
                    
                    data = data.split(",")
                    
                    # append the data to the global list so it will be added to the database
                    if len(data) == 5:
                        self.lock.acquire()
                        self.database.add_data(data)
                        self.lock.release()
                        
                    # forbidden process running
                    if len(data) == 2:
                        forbidden_process = data[1]

                        # Receive the number of packets to expect
                        num_packets_data = client_conn.recv(4)
                        num_packets = int.from_bytes(num_packets_data, byteorder="big")
                        print(num_packets)

                        # Receive the serialized data packets and reassemble them
                        received_data = b""
                        for _ in range(num_packets):
                            packet = client_conn.recv(4096)
                            print(packet)
                            received_data += packet
                        print(received_data.decode())
                        print(forbidden_process)

                except Exception as e:
                    break
        except:
            pass
        finally:
            # finally close the socket
            client_conn.close()
            self.update_database_connection(client_address, 'off')
            self.lock.acquire()
            global COMPUTERS
            COMPUTERS.pop(client_address[0])
            self.lock.release()
            print("DONE WITH THIS THREAD")


    def get_mac_address(self, ip_address):
        try:
            arp_command = ["arp", "-a"]
            output = subprocess.check_output(arp_command).decode()
            mac_address = output.split()
            mac_address = mac_address[mac_address.index(ip_address) + 1]
        except:
            mac_address = uuid.getnode()
            mac_address = ":".join(
                [
                    "{:02x}".format((mac_address >> elements) & 0xFF)
                    for elements in range(0, 8 * 6, 8)
                ][::-1]
            )
        return mac_address


    def update_database_connection(self, client_address, status):
        self.lock.acquire()
        print('here')
        self.database.update_connection(
            *[
                client_address[0],
                self.get_mac_address(client_address[0]),
                status,
            ]
        )
        self.lock.release()


    def run(self):
        while True:
            # accept a new client - main socket
            conn, addr = self.main_socket.accept()
            # accept a new client - alert socket
            alert_conn, alert_addr = self.alert_socket.accept()
            
            # put the socket in a global dict to ask for information
            self.lock.acquire()
            global COMPUTERS
            COMPUTERS[addr[0]] = conn
            self.lock.release()

            # thread that supplies client info
            info_thread = threading.Thread(
                target=self.get_comp_info,
                args=(
                    alert_conn,
                    alert_addr,
                ),
            )

            # start the thread to get information about the client's cpu' temp and memory
            info_thread.start()

def get_info_from_computer(self, ip, info):
    global COMPUTERS
    try:
        self.lock.acquire()
        socket = COMPUTERS[ip]
        self.lock.release()

        # Send the information request to the client
        socket.send(info.encode())

        # Receive the total number of packets
        total_packets = int(socket.recv(4).decode())

        # Receive and combine the data packets
        received_packets = []
        for packet_number in range(total_packets):
            data_packet = socket.recv(1064)
            received_packets.append(data_packet)

        # Combine the received packets
        combined_data = b"".join(received_packets)

        # Return the combined data to the caller
        return combined_data.decode()

    except:
        print('no such IP')

