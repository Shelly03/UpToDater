import socket
import threading
import sqlite3
import os
from threading import Lock

MAIN_PORT = 65432
ALERT_PORT = 65431

#TODO: ask what params to check in alerts, time between checks and if puting status in db is a good way
#TODO: add tables of ip stats - cpu, mem, temp
#TODO: add forbidhen procceses
DB_UPDATES = []


class server:
    def handle_db_updates(self):
        db_conn = sqlite3.connect(self.db_name)
        db_cursor = db_conn.cursor()

        while True:
            if len(DB_UPDATES) > 0:
                data = DB_UPDATES.pop(0)
                db_cursor.execute(f"SELECT * FROM {self.table_name} WHERE ip_address = ?", (data[0],))
                row = db_cursor.fetchone()
                colomns_names = list(data.keys())
                colomns_data = list(data.values())
                if row is not None:
                    self.database_command(db_cursor, f"UPDATE {self.table_name} SET {colomns_names[1:]} WHERE {self.colomns[0]}=?", list(data.values())[1:], data[self.colomns[0]])
                else:
                    self.database_command(db_cursor, f"INSERT INTO {self.table_name} {colomns_names} VALUES (?, ?)", data)
                db_conn.commit()
                

    def init_server(self):
        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_socket.bind(('0.0.0.0', MAIN_PORT))
        self.main_socket.listen(5)

        self.alert_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.alert_socket.bind(('0.0.0.0', ALERT_PORT))
        self.alert_socket.listen(5)
        self.alert_clients_socks = []


    def init_database(self):
        self.db_name = "ipconections.db"
        db_conn = sqlite3.connect(self.db_name)
        db_corsur = db_conn.cursor()
        self.table_name = 'ipAddresses'
        self.colomns = ['ip_address', 'connetion_status', 'cpu_status', ]
        db_corsur.execute(f'''CREATE TABLE if not exists {self.table_name}(
                                ip_address TEXT,
                                connection_status TEXT,
                                cpu_status TEXT DEFAULT 'good',
                                mem_status TEXT DEFAULT 'good'

                                ) ''')
        db_conn.commit()
        db_conn.close()
        self.update_db_thread = threading.Thread(target=self.handle_db_updates)

    def check_alerts(self, client_conn, client_address):
        try:
            db_conn = sqlite3.connect(self.db_name)
            db_cursor = db_conn.cursor()
            #TODO: handle closing (add global var to know if the thread is done)
            while True:
                status = client_conn.recv(1064).decode()
                aspect = status.split(':')[0]
                status = status.split(':')[1]
                colomn = aspect + '_' + 'status'
                #TODO: ask golan if this is a good way
                #self.database_command(db_cursor, f"UPDATE {self.table_name} SET {colomn}=? WHERE ip_address=?", (status, sock_addr[0]))
        except:
            pass

    def __init__(self):
        self.init_server()
        self.init_database()
        print('SERVER UP')

    def update_database_connection(self, client_address):
        DB_UPDATES.append({self.colomns[0] : client_address[0], self.colomns[1] : 'on'})

    def update_database_disconnection(self, client_address):
        DB_UPDATES.append({self.colomns[0] : client_address[0], self.colomns[1] : 'off'})

    def handle_client(self, client_main_socket, client_address):
        self.update_database_connection(client_address)
        try:
            while True:
                if (client_main_socket.recv(1064).decode() == 'bye'):
                    break
        except:
            pass
        finally:
            print('finally')
            client_main_socket.close()
            self.update_database_disconnection(client_address)

    def add_ip_to_db(self, client_addr):
        DB_UPDATES.append({self.colomns[0] : client_addr[0], self.colomns[1] : 'on'})

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

if __name__ == '__main__':
    server = server()
    server.run()
