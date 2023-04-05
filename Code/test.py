import sqlite3
from customtkinter import *
import tkinter as tk

class ServerGUI:
    def __init__(self, db_name='ipconections.db'):
        self.root = tk.Tk()
        self.root.title('Server GUI')
        self.db_name = db_name

        # Create a new database connection and cursor
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.c = self.conn.cursor()

        # Create the clients table if it doesn't exist
        self.c.execute('''CREATE TABLE IF NOT EXISTS clients
                            (ip_address text UNIQUE, connection_status text)''')
        self.conn.commit()

        # Create the parent frame and add a canvas widget to it
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill='both')
        self.canvas = CustomCanvas(self.frame, highlightthickness=0)
        self.canvas.pack(expand=True, fill='both')
        
        # Create a dictionary to store the computer icons and dots
        self.computers = {}


class ClientIcon:
    def __init__(self, canvas, ip_address, connection_status):
        self.canvas = canvas
        self.ip_address = ip_address
        self.connection_status = connection_status
        self.icon = PhotoImage(file='computer.gif')
        self.dot_on = PhotoImage(file='dot_on.gif')
        self.dot_off = PhotoImage(file='dot_off.gif')
        self.item_id = None
        self.dot_id = None

        self.draw()

    def draw(self):
        self.item_id = self.canvas.create_image(50, 50, image=self.icon, anchor=NW)
        self.update_status()

    def update_status(self):
        self.c.execute("SELECT connection_status FROM clients WHERE ip_address=?", (self.ip_address,))
        connection_status = self.c.fetchone()[0]
        if connection_status != self.connection_status:
            self.connection_status = connection_status
            if self.dot_id:
                self.canvas.delete(self.dot_id)
            if self.connection_status == 'on':
                self.dot_id = self.canvas.create_image(80, 80, image=self.dot_on, anchor=NW)
            else:
                self.dot_id = self.canvas.create_image(80, 80, image=self.dot_off, anchor=NW)

if __name__ == '__main__':
    app = ServerGUI()
    app.mainloop()