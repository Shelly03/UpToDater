import tkinter as tk
from tkinter import messagebox
import datetime
import pandas as pd
import snmp_server
import json
import ttkthemes as ttk


def parse_admin_file(file_path):
    admin_data = {
        "max_cpu": None,
        "max_cpu_temp": None,
        "max_mem": None,
        "forbidden_processes": [],
        "email": None
    }
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("max_cpu:"):
                admin_data["max_cpu"] = int(line.split(":")[1])
            elif line.startswith("max_cpu_temp:"):
                admin_data["max_cpu_temp"] = int(line.split(":")[1])
            elif line.startswith("max_mem:"):
                admin_data["max_mem"] = int(line.split(":")[1])
            elif line.startswith('"') and line.endswith('"') and line != '"process 1"':
                admin_data["forbidden_processes"].append(line.strip('"'))
            elif line.startswith("email:"):
                admin_data["email"] = line.split(":")[1].strip('"')
    
    return admin_data   

print(parse_admin_file(r'C:\Shelly\שלי - עמל ב עבודות\2022-2023\Cyber\פרויקט גמר\Code\sources\Files\Admin.txt'))