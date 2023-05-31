import threading
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
import sqlite3
from server import server
from cryptography.fernet import Fernet


class GUI:
    def refresh_data(self):
        db_conn = sqlite3.connect('ipconnections.db')
        db_cursor = db_conn.cursor()
        
        db_cursor.execute("SELECT * FROM Connections")
        self.data = db_cursor.fetchall()
        
        # Clear the existing treeview items
        self.tree.delete(*self.tree.get_children())

        # Insert updated items into the treeview
        for computer in self.data:
            ip = self.fernet.decrypt(computer[1]).decode()
            mac = self.fernet.decrypt(computer[2]).decode()
            if computer[3] == "on":
                parent = self.tree.insert(
                    "",
                    "end",
                    text="",
                    values=(ip, mac),
                    open=True,
                    tags="on",
                )
                self.tree.item(parent, image=self.on_icon, tags="on")
                self.create_tree_children(parent)
            else:
                parent = self.tree.insert(
                    "",
                    "end",
                    text="",
                    values=(ip, mac),
                    open=False,
                    tags="off",
                )
                self.tree.item(parent, image=self.off_icon, tags="off")

        # Schedule the next refresh
        self.root.after(1000, self.refresh_data)
        
    def __init__(self):
        # key
        file = open('key.key', 'rb') # rb = read bytes
        self.key  = file.read()
        file.close()
        self.fernet = Fernet(self.key)
        
        # contain an instance of the server in the GUI
        self.server = server()        
        server_thread = threading.Thread(target= self.server.run)
        server_thread.start()
        
        self.root = tk.Tk()
        self.root.title("NETVIGILANT")
        self.root.geometry("800x600")
        self.style = ThemedStyle(ttk.Style())
        self.style.set_theme("arc")

        # on and off icons
        self.on_icon = tk.PhotoImage(file="sources/Images/green_dot.png")
        self.off_icon = tk.PhotoImage(file="sources/Images/red_dot.png")

        # Create the sidebar
        self.sidebar = ttk.Frame(self.root, width=200)
        self.sidebar.pack(side="left", fill="y")

        # Logo
        self.light_logo = tk.PhotoImage(file="sources/Images/llogo.png")
        self.dark_logo = tk.PhotoImage(file="sources/Images/dlogo.png")
        self.logo_label = ttk.Label(self.sidebar, image=self.light_logo)
        self.logo_label.pack(pady=10)

        # Define the columns
        self.columns = [ "ip", "mac"]

        # Create a treeview widget
        self.tree = ttk.Treeview(self.root, selectmode= 'browse')
        self.tree.pack(side="left", fill="both", expand=True)
        
        self.tree['columns'] = self.columns
        self.tree['show'] = 'headings'
        self.tree['show'] = 'tree'

        # Configure the treeview
        self.tree.heading("#0", text="#")
        self.tree.heading("ip", text="IP") 
        self.tree.heading("mac", text="MAC")
        self.tree.column("#0", width=150, minwidth=10)
        self.tree.column("ip", width=150, minwidth=150)
        self.tree.column("mac", width=150, minwidth=150)

        # Set the icons for the TreeView
        self.tree.tag_configure("on", image=self.on_icon)
        self.tree.tag_configure("off", image=self.off_icon)

        self.refresh_data()
        self.root.after(1000, self.refresh_data)

        # Add a scrollbar to the treeview
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bind function to TreeviewSelect event
        self.tree.bind("<<TreeviewSelect>>", self.show_info)

        # Dark and light mode switch
        self.switch_value = True

        # Load light and dark mode images
        self.light = tk.PhotoImage(file="sources/Images/lightMode.png")
        self.dark = tk.PhotoImage(file="sources/Images/darkMode.png")

        # Create a button to toggle between light and dark themes
        self.switch = tk.Button(
            self.sidebar,
            image=self.light,
            bd=0,
            bg="white",
            activebackground="white",
            command=self.toggle,
        )
        self.switch.pack(padx=50, pady=10, side="bottom")

        self.root.mainloop()

    def toggle(self):
        if self.switch_value:
            self.style.set_theme("equilux")
            self.switch.config(
                image=self.dark, bg="#26242f", activebackground="#26242f"
            )
            self.logo_label.config(image=self.dark_logo)
            self.switch_value = False
        else:
            self.style.set_theme("arc")
            self.switch.config(image=self.light, bg="white", activebackground="white")
            self.logo_label.config(image=self.light_logo)
            self.switch_value = True

    def create_tree_children(self, parent):
        # Insert child items under each parent row
        self.tree.insert(parent, "end", text="Hardware Info")
        self.tree.insert(parent, "end", text="Net Info")
        self.tree.insert(parent, "end", text="Drives Info")
        self.tree.insert(parent, "end", text="Users Info")
        self.tree.insert(parent, "end", text="Connections Info")
        

    def show_info(self, event):
        try:
            # Get the selected item
            selected_item = self.tree.selection()[0]
            
            # Check if the selected item has a parent
            if self.tree.parent(selected_item):     
                
                # Get the parent item's IP address
                parent_item = self.tree.parent(selected_item)
                parent_ip = self.tree.item(parent_item)["values"][0]
                
                # Get the child item's text
                child_text = self.tree.item(selected_item, "text")
                
                # Get the data from the server using the parent IP address
                if child_text == 'Hardware Info':
                    print('here')
                    info = 'hardware'
                elif child_text == 'Net Info':
                    info = 'net'
                elif child_text == 'Drives Info':
                    info = 'drives'
                elif child_text == 'Users Info':
                    info = 'users'
                elif child_text == 'Connections Info':
                    info = 'connections'
                
                try:
                    data = self.server.get_info_from_computer(parent_ip, info)
                    print(data)
                    # Create a new window and display the data
                    new_window = tk.Toplevel(self.root)
                    text = "\n".join(data)  # Convert the data to a string
                    label = tk.Label(new_window, text=text)
                    label.pack()
                except Exception as e:
                    print(e)
                
        except:
            pass

if __name__ == "__main__":
    server_gui = GUI()