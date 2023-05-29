from joblib import load
import socket
import threading
import sqlite3
import os
from threading import Lock
import subprocess
import uuid

MAIN_PORT = 65432
ALERT_PORT = 65431

DB_UPDATES = []
IPS_ON = {}


class server:
    def handle_db_updates(self):
        # create connection and cursor for the db
        db_conn = sqlite3.connect(self.db_name)
        db_cursor = db_conn.cursor()

        while True:
            # if apdates list is not empty
            if len(DB_UPDATES) > 0:
                self.lock.acquire()
                # get the first update inserted (FIFO)
                data = DB_UPDATES.pop(0)

                if data[0] == self.conn_table_name:
                    db_cursor.execute(
                        f"SELECT * FROM {self.conn_table_name} WHERE {self.conn_table_colomns[1]} = ?",
                        (data[1],),
                    )
                    row = db_cursor.fetchone()
                    # check if new ip or not
                    if row is not None:
                        # if exist update connection status to the one given
                        db_cursor.execute(
                            f"UPDATE {self.conn_table_name} SET {self.conn_table_colomns[2]} = ? WHERE {self.conn_table_colomns[1]}=?",
                            (data[2], data[1]),
                        )
                    else:
                        # if not exist add the new ip to the table
                        print(data[1:])
                        db_cursor.execute(
                            f"INSERT INTO {self.conn_table_name} ({', '.join(self.conn_table_colomns[1:])}) VALUES (?, ?, ?)",
                            (data[1:]),
                        )

                elif data[0] == self.info_table_name:
                    # find the id of the ip
                    db_cursor.execute(
                        f"SELECT ID FROM {self.conn_table_name} WHERE {self.conn_table_colomns[1]} = ?",
                        (data[1],),
                    )
                    ip_id = db_cursor.fetchone()
                    # add the colomn with all of the info
                    values = [ip_id[0]] + data[2:]
                    db_cursor.execute(
                        f"INSERT INTO {self.info_table_name} ({', '.join(self.info_table_colomns)}) VALUES (?, ?, ?, ?, ?)",
                        (values),
                    )

                db_conn.commit()
                self.lock.release()

    def init_server(self):
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

        self.lock = Lock()

    def init_database(self):
        # create connection and cursor for the db
        self.db_name = "ipconnections.db"
        db_conn = sqlite3.connect(self.db_name)
        db_corsur = db_conn.cursor()

        self.conn_table_name = "Connections"
        self.info_table_name = "CompInfo"
        self.conn_table_colomns = [
            "id",
            "ip_address",
            "mac_address",
            "connection_status",
        ]
        self.info_table_colomns = ["id", "cpu", "temperature", "memory", "check_time"]

        # create connections table
        db_corsur.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.conn_table_name}  (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT NOT NULL,
                    mac_address TEXT NOT NULL,
                    connection_status TEXT NOT NULL)"""
        )

        # create computers info table
        db_corsur.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.info_table_name} (
                    id INTEGER NOT NULL,
                    cpu FLOAT NOT NULL,
                    temperature FLOAT NOT NULL,
                    memory FLOAT NOT NULL,
                    check_time TIMESTAMP not null,
                    FOREIGN KEY (id) REFERENCES ip_addresses (id))"""
        )

        # commit the changes and close the connection
        db_conn.commit()
        db_conn.close()

        # start thread that updates the table using global list
        self.update_db_thread = threading.Thread(target=self.handle_db_updates)
        self.update_db_thread.start()

    def get_comp_info(self, client_conn, client_address, main_sock_addr):
        while True:
            # if the connection is off the thread must end
            global IPS_ON
            if IPS_ON[main_sock_addr[0]] == False:
                print(IPS_ON)
                IPS_ON.pop(main_sock_addr[0])
                return

            try:
                data = client_conn.recv(1024).decode()

                data = data.split(",")
                # append the data to the global list so it will be added to the database
                if len(data) == 5:
                    DB_UPDATES.append([self.info_table_name, *data])
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

    def __init__(self):
        self.init_server()
        self.init_database()

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

    def update_database_connection(self, client_address):
        self.lock.acquire()
        DB_UPDATES.append(
            [
                self.conn_table_name,
                client_address[0],
                self.get_mac_address(client_address[0]),
                "on",
            ]
        )
        self.lock.release()

    def update_database_disconnection(self, client_address):
        self.lock.acquire()
        DB_UPDATES.append(
            [
                self.conn_table_name,
                client_address[0],
                self.get_mac_address(client_address[0]),
                "off",
            ]
        )
        self.lock.release()

    def handle_client(self, client_main_socket, client_address):
        # update database client has connected
        self.update_database_connection(client_address)
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
            # update database client has disconnected
            self.update_database_disconnection(client_address)

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
                    addr,
                ),
            )

            main_client_thread.start()
            info_thread.start()


if __name__ == "__main__":
    server = server()
    server.run()
