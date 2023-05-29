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

IPS_ON = {}


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
        while True:
            
            # if the connection is off the thread must end
            global IPS_ON
            if IPS_ON[client_address[0]] == False:
                IPS_ON.pop(client_address[0])
                break

            try:
                data = client_conn.recv(1024).decode()
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
                print(e)

        # finally close the socket
        client_conn.close()
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
        self.database.update_connection(
            *[
                client_address[0],
                self.get_mac_address(client_address[0]),
                status,
            ]
        )
        self.lock.release()


    def handle_client(self, client_main_socket, client_address):
        # update database client has connected
        self.update_database_connection(client_address, 'on')
        try:
            while True:
                if client_main_socket.recv(1064).decode() == "bye":
                    break

        except Exception as e:
            print("An error occurred in handle client:", str(e))
        finally:
            self.lock.acquire()
            global IPS_ON
            IPS_ON[client_address[0]] = False
            self.lock.release()
            # close the socket connection
            client_main_socket.close()
            # update database client has connected
            self.update_database_connection(client_address, 'off')

    def run(self):
        while True:
            # accept a new client
            conn, addr = self.main_socket.accept()
            alert_conn, alert_addr = self.alert_socket.accept()
            print("new client ", addr)
            print("allert line ", alert_addr)
            # thread that handles the client
            main_client_thread = threading.Thread(
                target=self.handle_client,
                args=(
                    conn,
                    addr,
                ),
            )

            # declare this ip as on so the info thread will know when the main client thread closes
            self.lock.acquire()
            global IPS_ON
            IPS_ON[addr[0]] = True
            self.lock.release()

            # thread that supplies client info
            info_thread = threading.Thread(
                target=self.get_comp_info,
                args=(
                    alert_conn,
                    alert_addr,
                ),
            )

            main_client_thread.start()
            info_thread.start()


if __name__ == "__main__":
    server = server()
    server.run()
