



import sqlite3


class database:

    def __init__(self):
        # create connection and cursor for the db
        self.db_name = "ipconnections.db"
        db_conn = sqlite3.connect(self.db_name)
        db_cursor = db_conn.cursor()

        # tables names
        self.conn_table_name = "Connections"
        self.info_table_name = "CompInfo"
        
        # columns for the table that describes the computers on the net
        self.conn_table_columns = [
            "id",
            "ip_address",
            "mac_address",
            "connection_status",
        ]
        
        # columns
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

    def update_connection(self, ip, mac, status):
        db_conn = sqlite3.connect(self.db_name)
        db_cursor = db_conn.cursor()
        # check if the ip is already in the table
        db_cursor.execute(
                        f"SELECT * FROM {self.conn_table_name} WHERE {self.conn_table_columns[1]} = ?",
                        (ip,),
                    )
        row = db_cursor.fetchone()
        
        # check if new ip or not
        if row is not None:
            # if exist update connection status to the one given
            db_cursor.execute(
                f"UPDATE {self.conn_table_name} SET {self.conn_table_columns[3]} = ? WHERE {self.conn_table_columns[1]}=?",
                (status, ip),
            )
        else:
            # if not exist add the new ip to the table
            db_cursor.execute(
                f"INSERT INTO {self.conn_table_name} ({', '.join(self.conn_table_columns[1:])}) VALUES (?, ?, ?)",
                (ip, mac, status),
            )
        db_conn.commit()
        db_conn.close()
        
    def add_data(self, data):
        print(data)
        db_conn = sqlite3.connect(self.db_name)
        db_cursor = db_conn.cursor()
        
        # find the id of the ip
        db_cursor.execute(
            f"SELECT ID FROM {self.conn_table_name} WHERE {self.conn_table_columns[1]} = ?",
            (data[0],),
        )
        wanted_id = db_cursor.fetchone()
        # add the colomn with all of the info
        values = [wanted_id[0]] + data[1:]
        db_cursor.execute(
            f"INSERT INTO {self.info_table_name} ({', '.join(self.info_table_columns)}) VALUES (?, ?, ?, ?, ?)",
            (values),
        )
