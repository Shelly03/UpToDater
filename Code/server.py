import socket
import threading
import sqlite3
import os
from threading import Lock

IP = '127.0.0.1'
MAIN_PORT = 65432
ALERT_PORT = 65431


class server:
    def init_server(self):
        self.lock = Lock()
        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_socket.bind(('0.0.0.0', MAIN_PORT))
        self.main_socket.listen(5)

        self.alert_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.alert_socket.bind(('0.0.0.0', ALERT_PORT))
        self.alert_socket.listen(5)
        self.alert_clients_socks = []

        self.db_name = "ipconections.db"

    def init_database(self):
        self.db_con = sqlite3.connect(self.db_name)
        self.db_corsur = self.db_con.cursor()
        self.table_name = 'ipAddresses'
        self.db_corsur.execute(f'''CREATE TABLE if not exists {self.table_name}(
                                ip_address TEXT,
                                connection_status TEXT,
                                cpu_status TEXT DEFAULT 'good',
                                mem_status TEXT DEFAULT 'good'

                                ) ''')
        self.db_corsur.execute(f"SELECT * FROM {self.table_name}")
        existing_client = self.db_corsur.fetchall()
        print(existing_client)
        self.db_con.commit()

    def check_alerts(self, sock_conn, sock_addr):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            while True:
                status = sock_conn.recv(1064).decode()
                aspect = status.split(':')[0]
                status = status.split(':')[1]
                colomn = aspect + '_' + 'status'
                #TODO: ask golan if this is a good way
                print('write1')
                self.database_command(cursor, f"UPDATE {self.table_name} SET {colomn}=? WHERE ip_address=?", (status, sock_addr[0]))

        except:
            pass
        finally:
            conn.commit()

    def __init__(self):
        self.init_server()
        self.init_database()
        print('SERVER UP')

    def update_database_connection(self, client_address):
        print('updating')
        # Create a new cursor for this thread
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Check if the client's IP address is already in the database
        cursor.execute(
            f"SELECT * FROM {self.table_name} WHERE ip_address=?", (client_address[0],))
        existing_client = cursor.fetchone()

        if existing_client:
            print('update2')
            # If the client's IP address is already in the database, update the row to indicate that the connection is on
            self.database_command(cursor, f"UPDATE {self.table_name} SET connection_status=? WHERE ip_address=?", ('on', client_address[0]))
        else:
            print('update3')
            # If the client's IP address is not in the database, insert a new row to indicate that the connection is on
            self.database_command(cursor, f"INSERT INTO {self.table_name} (ip_address, connection_status) VALUES (?, ?)", (client_address[0], 'on'))
        conn.commit()
        print('updated')

    def update_database_disconnection(self, client_address):
        # Create a new cursor for this thread
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        # Update the row to indicate that the connection is off
        print('update4')
        self.database_command(cursor, f"UPDATE {self.table_name} SET connection_status=? WHERE ip_address=?", ('off', client_address[0]))
        conn.commit()
        # Close the database connection
        conn.close()

    def handle_client(self, client_main_socket, client_address):
        try:
            self.update_database_connection(client_address)

            while True:
                if (client_main_socket.recv(1064).decode() == 'bye'):
                    break
        except:
            pass
        finally:
            print('finally')
            client_main_socket.close()
            self.update_database_disconnection(client_address)

    def add_ip_to_db(self, addr):
        db_con = sqlite3.connect("ipconections.db")
        db_corsur = db_con.cursor()
        print('update5')
        self.database_command(db_corsur, f'''INSERT INTO ipAddresses VALUES (
                "{addr[0]}", 
                "on" )''')
        db_con.commit()

    def run(self):
        while True:
            conn, addr = self.main_socket.accept()
            alert_conn, alert_addr = self.alert_socket.accept()
            main_client_thread = threading.Thread(
                target=self.handle_client, args=(conn, addr,))
            alert_thread = threading.Thread(
                target=self.check_alerts, args=(alert_conn, alert_addr,))
            print('alert thread on')

            main_client_thread.start()
            alert_thread.start()

    def database_command(self, cursor, command, args):
        self.lock.acquire()
        cursor.execute(command, args)
        self.lock.release()

if __name__ == '__main__':
    server = server()
    server.run()
