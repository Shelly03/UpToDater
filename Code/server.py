import socket
import threading
import sqlite3
import os

IP = '127.0.0.1'
PORT = 65432  

class server:
    def init_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((IP, PORT))
        self.socket.listen(5)
    
    def init_database(self):
        self.db_con = sqlite3.connect("ipconections.db")
        self.db_corsur = self.db_con.cursor()
        if not os.path.isfile("ipconections.db") : #FIXME: check if TABLE already exist not the db
            self.db_corsur.execute('''CREATE TABLE ipAddresses(
                                    ip TEXT,
                                    is_on TEXT
                                ) ''')
            self.db_con.commit()



    def __init__(self):
        self.init_server()
        self.init_database()
        print('SERVER UP')


    def handle_client(self, conn, addr):
        print(f'NEW CONNECTION > {addr}')
        
        
        connected = True
        
        while connected:
            pass
        
    def run(self):
        while True:
            conn, addr = self.socket.accept()
            thread = threading.Thread(target= self.handle_client, args= (conn, addr,))
            self.db_corsur.execute(f'''INSERT INTO ipcpnections VALUES (
                "{addr[0]}", 
                "on"
                )''') 
            #TODO: handle con closing and turning ip from "on" to "off"
            thread.start()
            
    def get_computers_online():
        pass
    
    def get_if_on(computer):
        pass
    

s = server()
s.run()
