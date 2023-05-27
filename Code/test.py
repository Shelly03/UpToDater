import psutil
import time

'''
class ComputerInfoSNMP:

    def handle_snmp_request(self, request):
        if request == 'cpu':
            return self.get_cpu_usage()
        elif request == 'gpu':
            return self.get_gpu_usage()
        elif request == 'ram':
            self.get_ram_usage()
        elif request == 'cpu temp':
            self.get_cpu_temperature()


    def get_cpu_temperature(self):
        temperature = psutil.sensors_temperatures().get('coretemp')[0].current
        return temperature

    def get_gpu_temperature(self):
        # Implement code to retrieve GPU temperature here
        # This will depend on the specific hardware and drivers being used
        temperature = 0
        return temperature

    def get_ram_usage(self):
        return psutil.cpu_percent(interval=1)

    def get_cpu_usage(self):
        load1, load5, load15 = psutil.getloadavg()
        cpu_usage = (load15/psutil.cpu_count()) * 100
        return cpu_usage
    
    def get_gpu_usage(self):
        return GPUtil.showUtilization()

    
s = ComputerInfoSNMP()
print(s.handle_snmp_request('cpu'))



import psutil
from datetime import datetime
import pandas as pd
import time
import os

def get_processes_info():
    # the list the contain all process dictionaries
    processes = []
    for process in psutil.process_iter():
    # get all process info in one shot (more efficient, without making separate calls for each attribute)
        with process.oneshot():
            # get the process id
            pid = process.pid
            
            if pid == 0:
                # Swapper or sched process, useless to see 
                continue
            
            # get the name of the file executed
            name = process.name()
            
            # get the time the process was spawned
            try:
                create_time = datetime.fromtimestamp(process.create_time())
            except OSError:
                # system processes, using boot time instead
                create_time = datetime.fromtimestamp(psutil.boot_time())
            
            try:
                # get the number of CPU cores that can execute this process
                cores = len(process.cpu_affinity())
            except psutil.AccessDenied:
                cores = 0
            
            # get the CPU usage percentage
            cpu_usage = process.cpu_percent()
            
            # get the status of the process (running, idle, etc.)
            status = process.status()
            
            try:
                # get the process "niceness" (priority)
                nice = int(process.nice())
            except psutil.AccessDenied:
                nice = 0
                
            try:
                # get the memory usage in mbytes
                memory_usage = process.memory_full_info().uss / 1000000
            except psutil.AccessDenied:
                memory_usage = 0

            #number of threads the process has
            n_threads = process.num_threads()
            
            # get the username of user spawned the process
            try:
                username = process.username()
            except psutil.AccessDenied:
                username = "N/A"
            processes.append({
            'pid': pid, 'name': name, 'create_time': create_time,
            'cores': cores, 'cpu_usage': cpu_usage, 'status': status, 'nice': nice,
            'memory_usage': memory_usage, 'n_threads': n_threads, 'username': username,
            })

    return processes

def construct_dataframe(processes):
    # convert to pandas dataframe
    df = pd.DataFrame(processes)
    # set the process id as index of a process
    df.set_index('pid', inplace=True)
    # convert to proper date format
    df['create_time'] = df['create_time'].apply(datetime.strftime, args=("%Y-%m-%d %H:%M:%S",))
    return df

df = construct_dataframe(get_processes_info())

df.to_csv('processes.csv', index=True)

# Open the text file with the default text editor
import os
os.system('start processes.csv')
'''

import tkinter as tk
from tkinter import ttk

# Create the main window
root = tk.Tk()
root.title("Tree View Example")

# Create a TreeView widget
tree = ttk.Treeview(root)

# Define the columns
tree["columns"] = ("Name", "Age")

# Format the columns
tree.column("#0", width=100)
tree.column("Name", width=150)
tree.column("Age", width=50)

# Create the headers
tree.heading("#0", text="Icon")
tree.heading("Name", text="Name")
tree.heading("Age", text="Age")

# Define the icons
icon_folder = tk.PhotoImage(file="folder_icon.png")
icon_file = tk.PhotoImage(file="file_icon.png")

# Add parent items
parent1 = tree.insert("", "end", image=icon_folder, text="Parent 1", values=("John Doe", 30))
parent2 = tree.insert("", "end", image=icon_folder, text="Parent 2", values=("Jane Smith", 25))

# Add child items
tree.insert(parent1, "end", image=icon_file, text="Child 1", values=("File 1", 10))
tree.insert(parent1, "end", image=icon_file, text="Child 2", values=("File 2", 12))
tree.insert(parent2, "end", image=icon_file, text="Child 3", values=("File 3", 8))
tree.insert(parent2, "end", image=icon_file, text="Child 4", values=("File 4", 9))

# Set the icons for the TreeView
tree.tag_configure("folder", image=icon_folder)
tree.tag_configure("file", image=icon_file)

# Pack the TreeView widget
tree.pack()

# Run the main loop
root.mainloop()





