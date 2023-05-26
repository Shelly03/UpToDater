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
from PIL import Image

class MyGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title('NETVIGILANT')
        self.geometry("1100x580")

        # sidebar
        self.sidebar_frame = ttk.Frame(self, width=140)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Added line
                
        # logo
        self.logo = Image.open("sources\Images\llogo.png")
        self.labelimage = ttk.Label(master=self.sidebar_frame, image=self.logo, anchor="nw")

        # Grid positioning
        self.labelimage.grid(row=0, column=0, sticky="nw")

        # change theme
        self.appearance_mode_label = ttk.Label(self.sidebar_frame, text="theme:", anchor="sw")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionmenu = ttk.OptionMenu(self.sidebar_frame, tk.StringVar(), "Dark", "Light", "Dark", "System", command=self.change_theme)
        self.appearance_mode_optionmenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        
        # add scaling
        self.scaling_label = ttk.Label(self.sidebar_frame, text="UI Scaling:", anchor="sw")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionmenu = ttk.OptionMenu(self.sidebar_frame, tk.StringVar(), "100%", "80%", "90%", "100%", "110%", "120%", command=self.change_scaling)
        self.scaling_optionmenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        
        self.appearance_mode_optionmenu["menu"].config(bg="white", fg="black")  # Set menu background and foreground colors
        self.scaling_optionmenu["menu"].config(bg="white", fg="black")  # Set menu background and foreground colors
        
        self.appearance_mode_optionmenu.set("Dark")
        self.scaling_optionmenu.set("100%")

    def change_theme(self, selected_mode):
        if selected_mode == "Light":
            self.configure(bg="white")
            self.labelimage.configure(bg="white")
            self.appearance_mode_label.configure(bg="white", fg="black")
            self.appearance_mode_optionmenu.configure(bg="white", fg="black")
            self.scaling_label.configure(bg="white", fg="black")
            self.scaling_optionmenu.configure(bg="white", fg="black")
            self.logo = Image.open("sources\Images\llogo.png")  # Change the logo image to light mode image
            self.labelimage.configure(image=self.logo)
        elif selected_mode == "Dark":
            self.configure(bg="black")
            self.labelimage.configure(bg="black")
            self.appearance_mode_label.configure(bg="black", fg="white")
            self.appearance_mode_optionmenu.configure(bg="black", fg="white")
            self.scaling_label.configure(bg="black", fg="white")
            self.scaling_optionmenu.configure(bg="black", fg="white")
            self.logo = Image.open("sources\Images\dlogo.png")  # Change the logo image to dark mode image
            self.labelimage.configure(image=self.logo)

    def change_scaling(self, selected_scaling):
        if selected_scaling == "80%":
            # Apply scaling of 80%
            self.configure(scale_factor=0.8)
        elif selected_scaling == "90%":
            # Apply scaling of 90%
            self.configure(scale_factor=0.9)
        elif selected_scaling == "100%":
            # Apply scaling of 100%
            self.configure(scale_factor=1.0)
        elif selected_scaling == "110%":
            # Apply scaling of 110%
            self.configure(scale_factor=1.1)
        elif selected_scaling == "120%":
            # Apply scaling of 120%
            self.configure(scale_factor=1.2)

    def create_options(self):
        # Create additional options
        pass

# Create the main window
app = MyGUI()

# Start the Tkinter event loop
app.mainloop()