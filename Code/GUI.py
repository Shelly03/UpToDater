import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
import sqlite3


class ServerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NETVIGILANT")
        self.root.geometry("800x600")
        self.style = ThemedStyle(ttk.Style())
        self.style.set_theme("arc")

        # on and off icons
        self.on_icon = tk.PhotoImage(file="Code/sources/Images/green_dot.png")
        self.off_icon = tk.PhotoImage(file="Code/sources/Images/red_dot.png")

        # Create the sidebar
        self.sidebar = ttk.Frame(self.root, width=200)
        self.sidebar.pack(side="left", fill="y")

        # Logo
        self.light_logo = tk.PhotoImage(file="Code/sources/Images/llogo.png")
        self.dark_logo = tk.PhotoImage(file="Code/sources/Images/dlogo.png")
        self.logo_label = ttk.Label(self.sidebar, image=self.light_logo)
        self.logo_label.pack(pady=10)

        self.db_conn = sqlite3.connect("ipconnections.db")
        self.db_cursor = self.db_conn.cursor()

        self.db_cursor.execute("SELECT * FROM Connections")
        self.data = self.db_cursor.fetchall()

        # Define the columns
        self.columns = ["status", "ip", "mac"]

        # Create a treeview widget
        self.tree = ttk.Treeview(self.root, columns=self.columns, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)

        # Configure the treeview
        self.tree.heading("#0", text="#")
        self.tree.heading("status", text="Status")
        self.tree.heading("ip", text="IP")
        self.tree.heading("mac", text="MAC")
        self.tree.column("#0", width=20, minwidth=10)
        self.tree.column("status", width=100)
        self.tree.column("ip", width=150, minwidth=150)
        self.tree.column("mac", width=150, minwidth=150)

        # Set the icons for the TreeView
        self.tree.tag_configure("on", image=self.on_icon)
        self.tree.tag_configure("off", image=self.off_icon)

        # Insert items into the treeview
        for computer in self.data:
            if computer[3] == "on":
                parent = self.tree.insert(
                    "",
                    "end",
                    text="",
                    values=("ON", computer[1], computer[2]),
                    open=True,
                    tags="on",
                )
                self.tree.item(parent, image=self.on_icon, tags="on")
            else:
                parent = self.tree.insert(
                    "",
                    "end",
                    text="",
                    values=("OFF", computer[1], computer[2]),
                    open=True,
                    tags="off",
                )
                self.tree.item(parent, image=self.off_icon, tags="off")

            # Insert child items under each parent row
            self.tree.insert(parent, "end", text="Load Info")
            self.tree.insert(parent, "end", text="Net Info")
            self.tree.insert(parent, "end", text="Stats Info")

        # Add a scrollbar to the treeview
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Dark and light mode switch
        self.switch_value = True

        # Load light and dark mode images
        self.light = tk.PhotoImage(file="Code/sources/Images/lightMode.png")
        self.dark = tk.PhotoImage(file="Code/sources/Images/darkMode.png")

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


if __name__ == "__main__":
    server_gui = ServerGUI()
