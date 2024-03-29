import json
import uuid
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
        try:
            while True:
                try:
                    data = client_conn.recv(4096).decode()

                    if data == "bye":
                        break

                    data = data.split(",")

                    # append the data to the global list so it will be added to the database
                    if len(data) == 4:
                        print('before lock 54')
                        self.lock.acquire()
                        self.database.add_data([client_address[0], *data])
                        self.lock.release()
                        print('after lock 58')

                    # forbidden process running
                    if len(data) == 2:
                        forbidden_process = data[1]

                        # Receive the number of packets to expect
                        num_packets_data = client_conn.recv(4)
                        num_packets = int.from_bytes(num_packets_data, byteorder="big")

                        # Receive the serialized data packets and reassemble them
                        received_data = b""
                        for _ in range(num_packets):
                            packet = client_conn.recv(4096)
                            received_data += packet
                        print(received_data.decode())
                        print(forbidden_process)

                except WindowsError:
                    break
                except Exception as e:
                    print(e)
        except Exception as e:
            pass
        finally:
            # finally close the socket
            client_conn.close()
            self.update_database_connection(client_address, "off")
            print('before lock 82')
            self.lock.acquire()
            global COMPUTERS
            COMPUTERS.pop(client_address[0])
            self.lock.release()
            print('after lock 87')
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
        self.database.update_connection(
            *[
                client_address[0],
                self.get_mac_address(client_address[0]),
                status,
            ]
        )

    def run(self):
        while True:
            # accept a new client - main socket
            conn, addr = self.main_socket.accept()
            # accept a new client - alert socket
            alert_conn, alert_addr = self.alert_socket.accept()

            print("> NEW CONNECTION ", addr)

            # put the socket in a global dict to ask for information
            print('before lock 125')
            self.lock.acquire()
            self.update_database_connection(addr, "on")
            global COMPUTERS
            COMPUTERS[addr[0]] = conn
            self.lock.release()
            print('after lock 127')

            conn.send(json.dumps(self.database.get_admin_settings()).encode())

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
        print('here')
        global COMPUTERS
        try:
            print('before lock 148')
            self.lock.acquire()
            socket = COMPUTERS[ip]
            self.lock.release()
            print('after lock 150')

            # Send the information request to the client
            print(ip, " sent ", info)
            socket.send(info.encode())
            print("sent", info)

            '''# Receive the total number of packets
            got_number_of_packets = False
            total_packets = 0
            while not got_number_of_packets:
                try:
                    total_packets = int(socket.recv(1024))
                    print(total_packets)
                    got_number_of_packets = True
                except:
                    pass
            # Receive and combine the data packets
            received_packets = []
            for packet_number in range(total_packets):
                data_packet = socket.recv(1024)
                print("got packet")
                received_packets.append(data_packet)
            print("done")

            # Combine the received packets
            combined_data = b"".join(received_packets)

            # Return the combined data to the caller
            print(combined_data.decode())
            return combined_data.decode()'''
            data = socket.recv(65536).decode()
            print(data)
            print(type(data))
            return data
        
        except Exception as e:
            print(e)

