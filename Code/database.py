
import sqlite3
from cryptography.fernet import Fernet

class database:

    def __init__(self):
        # key
        file = open(r'sources\Files\key.key', 'rb') # rb = read bytes
        self.key  = file.read()
        file.close()
        self.fernet = Fernet(self.key)
        
        # create connection and cursor for the db
        self.db_name = "ipconnections.db"
        db_conn = sqlite3.connect(self.db_name)
        db_cursor = db_conn.cursor()

        # tables names
        self.conn_table_name = "Connections"
        self.info_table_name = "CompInfo"
        
        # columns for the table that describes the different computers on the net
        self.conn_table_columns = [
            "id",
            "ip_address",
            "mac_address",
            "connection_status",
        ]
        
        # columns for the table that saves the computer's updates on their performance
        self.info_table_columns = [
            "id", 
            "cpu", 
            "temperature", 
            "memory", 
            "check_time"
        ]

        # create connections table
        db_cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.conn_table_name}  (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT NOT NULL,
                    mac_address TEXT NOT NULL,
                    connection_status TEXT NOT NULL)"""
        )
        
        db_cursor.execute(f"UPDATE {self.conn_table_name} SET connection_status = 'off'")

        # create computers info table
        db_cursor.execute(
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

    def get_id(self, ip, rows):
        for row in rows:
            decrypted_ip = self.fernet.decrypt(row[1]).decode()
            if decrypted_ip == ip:
                return row[0]


    def update_connection(self, ip, mac, status):
        # create new connection and cursor
        db_conn = sqlite3.connect(self.db_name)
        db_cursor = db_conn.cursor()
        
        
        encrypted_ip = self.fernet.encrypt(ip.encode())
        encrypted_mac = self.fernet.encrypt(mac.encode())
                
        # check if the ip is already in the table
        db_cursor.execute(
                        f"SELECT {self.conn_table_columns[0]},{self.conn_table_columns[1]} FROM {self.conn_table_name}",
                    )
        rows = db_cursor.fetchall()
        
        wanted_id = self.get_id(ip, rows)
        
        # check if new ip or not
        if wanted_id is not None:
            # if exist update connection status to the one given
            db_cursor.execute(
                f"UPDATE {self.conn_table_name} SET {self.conn_table_columns[3]} = ? WHERE {self.conn_table_columns[0]}=?",
                (status, wanted_id),
            )
        else:
            # if not exist add the new ip to the table
            db_cursor.execute(
                f"INSERT INTO {self.conn_table_name} ({', '.join(self.conn_table_columns[1:])}) VALUES (?, ?, ?)",
                (encrypted_ip, encrypted_mac, status),
            )
        db_conn.commit()
        db_conn.close()
        
    def add_data(self, data):
        # create new connection and cursor
        db_conn = sqlite3.connect(self.db_name)
        db_cursor = db_conn.cursor()
        
        # find the id of the ip
        db_cursor.execute(
            f"SELECT {self.conn_table_columns[0]}, {self.conn_table_columns[1]} FROM {self.conn_table_name}",
        )
        rows = db_cursor.fetchall()

        wanted_id = self.get_id(data[0], rows)
        
        # add the colomn with all of the info
        values = [wanted_id] + data[1:]
        db_cursor.execute(
            f"INSERT INTO {self.info_table_name} ({', '.join(self.info_table_columns)}) VALUES (?, ?, ?, ?, ?)",
            (values),
        )
        db_conn.commit()
        db_conn.close()

