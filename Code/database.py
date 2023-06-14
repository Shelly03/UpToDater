import sqlite3
from cryptography.fernet import Fernet

ADMIN_SETTINGS_PATH = "sources\Files\Admin.txt"


class database:
    def __init__(self):
        # key
        file = open(r"sources\Files\key.key", "rb")  # rb = read bytes
        self.key = file.read()
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
        self.info_table_columns = ["id", "cpu", "temperature", "memory", "check_time"]

        # create connections table
        db_cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.conn_table_name}  (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT NOT NULL,
                    mac_address TEXT NOT NULL,
                    connection_status TEXT NOT NULL)"""
        )

        db_cursor.execute(
            f"UPDATE {self.conn_table_name} SET connection_status = 'off'"
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

    def get_id(self, ip, rows):
        print("ip: ", ip)
        for row in rows:
            decrypted_ip = self.fernet.decrypt(row[1]).decode()
            print("dec ip: ", decrypted_ip)
            if decrypted_ip == ip:
                return row[0]
        return "not found"

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
        print("connected")
        # find the id of the ip
        db_cursor.execute(
            f"SELECT {self.conn_table_columns[0]}, {self.conn_table_columns[1]} FROM {self.conn_table_name}",
        )
        rows = db_cursor.fetchall()
        print("got rows ", rows)
        wanted_id = self.get_id(data[0], rows)
        print("wanted id: ", wanted_id)
        # add the row with all of the info
        values = [wanted_id] + data[1:]
        db_cursor.execute(
            f"INSERT INTO {self.info_table_name} ({', '.join(self.info_table_columns)}) VALUES (?, ?, ?, ?, ?)",
            (values),
        )
        print("inserted data")
        db_conn.commit()
        db_conn.close()

    def get_admin_settings(self):
        admin_data = {
            "max_cpu": None,
            "max_cpu_temp": None,
            "max_mem": None,
            "forbidden_processes": [],
            "email": None,
        }

        with open(ADMIN_SETTINGS_PATH, "r") as file:
            lines = file.readlines()

            for line in lines:
                line = line.strip()

                if line.startswith("max_cpu:"):
                    admin_data["max_cpu"] = int(line.split(":")[1])
                elif line.startswith("max_cpu_temp:"):
                    admin_data["max_cpu_temp"] = int(line.split(":")[1])
                elif line.startswith("max_mem:"):
                    admin_data["max_mem"] = int(line.split(":")[1])
                elif (
                    line.startswith('"')
                    and line.endswith('"')
                    and line != '"process 1"'
                ):
                    admin_data["forbidden_processes"].append(line.strip('"'))
                elif line.startswith("email:"):
                    admin_data["email"] = line.split(":")[1].strip('"')

        return admin_data
