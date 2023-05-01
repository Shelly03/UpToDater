import socket
import threading
import sqlite3
import os

IP = '127.0.0.1'
PORT = 65432

class server:
    def init_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('0.0.0.0', PORT))
        self.socket.listen(5)

    def init_database(self):
        self.db_name = "ipconections.db"
        self.db_con = sqlite3.connect(self.db_name)
        self.db_corsur = self.db_con.cursor()
        self.table_name = 'ipAddresses'
        self.db_corsur.execute(f'''CREATE TABLE if not exists {self.table_name}(
                                ip_address TEXT,
                                connection_status TEXT
                                ) ''')
        self.db_con.commit()


    def __init__(self):
        self.init_server()
        self.init_database()
        print('SERVER UP')


    def handle_client(self, client_socket, client_address):
        # Create a new cursor for this thread
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
            
        try:
            # Check if the client's IP address is already in the database
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE ip_address=?", (client_address[0],))
            existing_client = cursor.fetchone()

            if existing_client:
                # If the client's IP address is already in the database, update the row to indicate that the connection is on
                cursor.execute(f"UPDATE {self.table_name} SET connection_status=? WHERE ip_address=?", ('on', client_address[0]))
                print(client_address[0])
            else:
                # If the client's IP address is not in the database, insert a new row to indicate that the connection is on
                cursor.execute(f"INSERT INTO {self.table_name} (ip_address, connection_status) VALUES (?, ?)", (client_address[0], 'on'))
            conn.commit()

            while True:
                if(client_socket.recv(1064).decode() == 'bye'):
                    break
        
        except Exception as e:
            print(e)
            
        finally:
            print('finally')
            # Update the row to indicate that the connection is off
            cursor.execute(f"UPDATE {self.table_name} SET connection_status=? WHERE ip_address=?", ('off', client_address[0]))
            conn.commit()
            # Close the client socket
            client_socket.close()
            # Close the database connection
            conn.close()
            
    def add_ip_to_db(self, addr):
        db_con = sqlite3.connect("ipconections.db")
        db_corsur = db_con.cursor()
        db_corsur.execute(f'''INSERT INTO ipAddresses VALUES (
                "{addr[0]}", 
                "on"
                )''') 
        db_con.commit()
        
    def run(self):
        while True:
            conn, addr = self.socket.accept()
            thread = threading.Thread(target= self.handle_client, args= (conn, addr,))

            thread.start()

if __name__ == '__main__':
    server = server()
    server.run()

