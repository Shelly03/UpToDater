import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
import sqlite3

def open_new_window(event):
    selected_item = tree.selection()
    if selected_item:
        item_text = tree.item(selected_item, "text")
        item_info = tree.item(selected_item, "values")[0]
        new_window = tk.Toplevel(root)
        new_window.title("New Window")
        new_window.geometry("400x300")
        label = ttk.Label(new_window, text=f"Button Text: {item_text}\nButton Info: {item_info}")
        label.pack(pady=10)
        back_button = ttk.Button(new_window, text="Go Back", command=new_window.destroy)
        back_button.pack(pady=10)

root = tk.Tk()
root.title("NETVIGILANT")
root.geometry("800x600")
style = ThemedStyle(ttk.Style())
style.set_theme("arc")

# on and off icons
on_icon = tk.PhotoImage(file="Code/sources/Images/green_dot.png")
off_icon = tk.PhotoImage(file="Code/sources/Images/red_dot.png")

# Create the sidebar
sidebar = ttk.Frame(root, width=200)
sidebar.pack(side="left", fill="y")

# Logo
light_logo = tk.PhotoImage(file="Code/sources/Images/llogo.png")
dark_logo = tk.PhotoImage(file="Code/sources/Images/dlogo.png")
logo_label = ttk.Label(sidebar, image=light_logo)
logo_label.pack(pady=10)

db_conn = sqlite3.connect('ipconnections.db')
db_cursor = db_conn.cursor()

db_cursor.execute('SELECT * FROM Connections')
data = db_cursor.fetchall()

# Define the columns
columns = ['ip', 'mac']

# Create a treeview widget
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.pack(side="left", fill="both", expand=True)

# Configure the treeview
tree.heading("#0", text="Status")
tree.heading("ip", text="IP")
tree.heading("mac", text="MAC")
tree.column("#0", width=100)
tree.column("ip", width=150, minwidth=150)
tree.column("mac", width=150, minwidth=150)

# Set the icons for the TreeView
tree.tag_configure("on", image=on_icon)
tree.tag_configure("off", image=off_icon)

# Insert items into the treeview
for computer in data:
    if computer[3] == 'on':
        row = tree.insert("", "end",text='Computer', values=(computer[1], computer[2]), open=True)
    else:
        row = tree.insert("", "end", text='Computer', values=(computer[1], computer[2]), open=True)

    # Insert child items under each parent row
    tree.insert(row, "end", text='Load Info')
    tree.insert(row, "end", text='Net Info')
    tree.insert(row, "end", text='Stats Info')

# Add a scrollbar to the treeview
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
scrollbar.pack(side="right", fill="y")
tree.configure(yscrollcommand=scrollbar.set)

# Dark and light mode switch
switch_value = True

def toggle():
    global switch_value
    if switch_value:
        style.set_theme("equilux")
        switch.config(image=dark, bg="#26242f", activebackground="#26242f")
        logo_label.config(image=dark_logo)
        switch_value = False
    else:
        style.set_theme("arc")
        switch.config(image=light, bg="white", activebackground="white")
        logo_label.config(image=light_logo)
        switch_value = True

# Load light and dark mode images
light = tk.PhotoImage(file="Code/sources/Images/lightMode.png")
dark = tk.PhotoImage(file="Code/sources/Images/darkMode.png")

# Create a button to toggle between light and dark themes
switch = tk.Button(sidebar, image=light, bd=0, bg="white", activebackground="white", command=toggle)
switch.pack(padx=50, pady=10, side="bottom")

root.mainloop()