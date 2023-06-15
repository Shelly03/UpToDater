import datetime
import json
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkthemes import ThemedStyle
import sqlite3
from server import server
from cryptography.fernet import Fernet
import pandas as pd
import WOL


class GUI:
    def __init__(self):
        # key
        file = open("sources/files/key.key", "rb")  # rb = read bytes
        self.key = file.read()
        file.close()
        self.fernet = Fernet(self.key)

        # contain an instance of the server in the GUI
        self.server = server()
        server_thread = threading.Thread(target=self.server.run)
        server_thread.start()

        self.root = tk.Tk()
        self.root.title("NETVIGILANT")
        self.root.geometry("800x600")
        self.style = ThemedStyle(ttk.Style())
        self.style.set_theme("arc")

        # on and off icons
        self.on_icon = tk.PhotoImage(file="sources/Images/green_dot.png")
        self.off_icon = tk.PhotoImage(file="sources/Images/red_dot.png")
        self.dark_on_icon = tk.PhotoImage(file="sources/Images/dark_green_dot.png")
        self.dark_off_icon = tk.PhotoImage(file="sources/Images/dark_red_dot.png")

        # Create the sidebar
        self.sidebar = ttk.Frame(self.root, width=200)
        self.sidebar.pack(side="left", fill="y")

        # Logo
        self.light_logo = tk.PhotoImage(file="sources/Images/llogo.png")
        self.dark_logo = tk.PhotoImage(file="sources/Images/dlogo.png")
        self.logo_label = ttk.Label(self.sidebar, image=self.light_logo)
        self.logo_label.pack(pady=10)

        # Define the columns
        self.columns = ["ip", "mac"]

        # Create a treeview widget
        self.tree = ttk.Treeview(self.root, selectmode="browse")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree["columns"] = self.columns
        self.tree["show"] = "headings"
        self.tree["show"] = "tree"

        # Configure the treeview
        self.tree.heading("#0", text="#")
        self.tree.heading("ip", text="IP")
        self.tree.heading("mac", text="MAC")
        self.tree.column("#0", width=150, minwidth=10)
        self.tree.column("ip", width=150, minwidth=150)
        self.tree.column("mac", width=150, minwidth=150)

        # Set the icons for the TreeView
        self.initialize_icons()
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
        self.dark = tk.PhotoImage(file="sources/Images/darkdarkMode.png")

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

    def refresh_data(self):
        db_conn = sqlite3.connect("ipconnections.db")
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

        # Create the right-click context menu
        self.wol_menu = tk.Menu(self.root, tearoff=0)

        # Add "Wake on LAN" option to the menu
        self.wol_menu.add_command(label="Wake on LAN")

        # Bind right-click event to the treeview
        self.tree.bind("<Button-3>", self.wol_right_click)

        # Attach the menu to the treeview
        self.tree.bind("<Button-3>", lambda event: self.tree.focus(), add="+")
        self.tree.bind(
            "<Button-3>",
            lambda event: self.wol_menu.post(event.x_root, event.y_root),
            add="+",
        )

        # Schedule the next refresh
        self.root.after(1000, self.refresh_data)

    def wol_right_click(self, event):
        item = self.tree.focus()  # Get the selected item
        if (
            item and self.tree.item(item, "tags") == "off"
        ):  # Check if the selected item has "off" tag
            mac_address = self.tree.set(
                item, "mac"
            )  # Get the MAC address from the selected item
            self.wol_menu.entryconfigure(
                "Wake on LAN", command=lambda: WOL.send_magic_packet(mac_address)
            )
            self.wol_menu.tk_popup(event.x_root, event.y_root)

    def initialize_icons(self):
        # Initialize the on and off icons based on the current theme
        if self.style.theme_use() == "equilux":
            self.on_icon = tk.PhotoImage(file="sources/Images/dark_green_dot.png")
            self.off_icon = tk.PhotoImage(file="sources/Images/dark_red_dot.png")
        else:
            self.on_icon = tk.PhotoImage(file="sources/Images/green_dot.png")
            self.off_icon = tk.PhotoImage(file="sources/Images/red_dot.png")

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

        self.initialize_icons()  # Update the icons based on the new theme
        self.tree.tag_configure("on", image=self.on_icon)
        self.tree.tag_configure("off", image=self.off_icon)

    def create_tree_children(self, parent):
        # Insert child items under each parent row
        self.tree.insert(parent, "end", text="Hardware Info")
        self.tree.insert(parent, "end", text="Network Info")
        self.tree.insert(parent, "end", text="Drives Info")
        self.tree.insert(parent, "end", text="Users Info")
        self.tree.insert(parent, "end", text="Running Processes Info")

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

                # Create a new window and display the data
                new_window = tk.Toplevel(self.root)

                # Get the data from the server using the parent IP address
                if child_text == "Hardware Info":
                    self.display_hardware_info(
                        self.server.get_info_from_computer(parent_ip, "hardware"),
                        new_window,
                    )
                elif child_text == "Network Info":
                    self.display_network_info(
                        self.server.get_info_from_computer(parent_ip, "net"), new_window
                    )
                elif child_text == "Drives Info":
                    self.display_drives_info(
                        self.server.get_info_from_computer(parent_ip, "drives"),
                        new_window,
                    )
                elif child_text == "Users Info":
                    self.display_users_info(
                        self.server.get_info_from_computer(parent_ip, "users"),
                        new_window,
                    )
                elif child_text == "Running Processes Info":
                    self.open_file_question(parent_ip, new_window)

        except:
            pass

    def display_hardware_info(self, data, window):
        # convert the string to a dict
        data = json.loads(data)

        window.title("Hardware Infornation")

        tree = ttk.Treeview(
            window,
            columns=(
                "",
                "",
            ),
            show="headings",
        )

        for key, value in data.items():
            tree.insert(
                "",
                tk.END,
                values=(
                    key,
                    value,
                ),
            )
        tree.pack(expand=True, fill="both")

    def display_users_info(self, users, window):
        # convert the string to a list
        users = json.loads(users)

        window.title("Users Infornation")

        tree = ttk.Treeview(
            window,
            columns=(
                "",
                "",
            ),
            show="headings",
        )

        for i in range(len(users)):
            tree.insert(
                "",
                tk.END,
                values=(
                    f"User{i+1}",
                    users[i],
                ),
            )
        tree.pack(expand=True, fill="both")

    def display_network_info(self, data, window):
        # convert the string to a dict
        data = json.loads(data)

        window.title("Network Infornation")

        tree = ttk.Treeview(
            window,
            columns=(
                "",
                "",
            ),
            show="headings",
        )

        for key, value in data.items():
            row = tree.insert(
                "",
                tk.END,
                values=(
                    key.split(":")[0],
                    value,
                ),
            )

        tree.pack(expand=True, fill="both")

    def display_drives_info(self, drives, window):
        window.title("Drives Infornation")
        tree = ttk.Treeview(
            window,
            columns=(
                "",
                "",
            ),
            show="tree headings",
        )

        # convert the string to a list of dicts
        drives = [json.loads(idx.replace("'", '"')) for idx in [drives]]

        for drive in drives[0]:
            parent = tree.insert("", tk.END, values=(drive["name"]), open=True)
            for key, value in drive.items():
                if key != "name":
                    tree.insert(parent, tk.END, values=(key, value))
        tree.pack(expand=True, fill="both")

    def create_excel_file(self, data, ip):
        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Create folder path
        folder_path = r"running processes info"

        # Create Excel file name
        file_name = f"processes of {ip} - {timestamp}.xlsx"

        # convert to pandas dataframe
        print(data)
        data = [json.loads(idx.replace("'", '"')) for idx in [data]]
        print(type(data))
        df = pd.DataFrame(data[0])
        print(df)

        # Create Excel file
        file_path = f"{folder_path}/{file_name}"
        df.to_excel(file_path, index=False)
        print("made file")

        # Open Excel file
        try:
            pd.ExcelFile(file_path)
        except FileNotFoundError:
            messagebox.showerror("Error", "File not found.")
        else:
            messagebox.showinfo("Success", "Excel file created successfully.")

    def open_file_question(self, ip, new_window):
        def handle_create_file():
            print("got in jsndle create file")
            processes = self.server.get_info_from_computer(ip, "running processes")
            self.create_excel_file(processes, ip)
            new_window.destroy()

        def handle_cancel():
            new_window.destroy()

        new_window.title("Open Excel File")

        label = tk.Label(
            new_window, text="Do you want to get the information in an Excel file?"
        )
        label.pack(padx=10, pady=10)

        button_frame = tk.Frame(new_window)
        button_frame.pack(padx=10, pady=10)

        create_file_button = tk.Button(
            button_frame, text="Yes, create a file", command=handle_create_file
        )
        create_file_button.pack(side=tk.LEFT)

        cancel_button = tk.Button(button_frame, text="Cancel", command=handle_cancel)
        cancel_button.pack(side=tk.LEFT)


if __name__ == "__main__":
    server_gui = GUI()
