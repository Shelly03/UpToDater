import sqlite3
import customtkinter
import tkinter as tk
from tkinter import ttk
import server
from PIL import Image,ImageTk
import sys

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")
        
class ServerGUI(customtkinter.CTk):
    
    def __init__(self, db_name='ipconections.db'):
        super().__init__()
        
        self.title('NETVIGILANT')
        self.geometry("1100x580")

        # images
        self.comp_icon = customtkinter.CTkImage(Image.open("sources\Images\computer_icon.png"))

        # sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nws")

        # logo
        self.logo = customtkinter.CTkImage(light_image=Image.open("sources\Images\llogo.png"),
                                        dark_image=Image.open("sources\Images\dlogo.png"),
                                        size=(200, 200))
        self.labelimage = customtkinter.CTkLabel(master=self.sidebar_frame, text=None, image=self.logo, anchor="nw")

        # Grid positioning
        self.labelimage.grid(row=0, column=0, sticky="nw")

        # change theme
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="theme:", anchor="sw")
        self.appearance_mode_label.grid(padx=20, pady=(10, 0), sticky="sw")
        self.appearance_mode_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_theme)
        self.appearance_mode_optionmenu.grid(padx=20, pady=(10, 10), sticky="sw")

        # add scaling
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="sw")
        self.scaling_label.grid(padx=20, pady=(10, 0), sticky="sw")
        self.scaling_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling)
        self.scaling_optionmenu.grid(padx=20, pady=(10, 20), sticky="sw")

        self.grid_rowconfigure(0, weight=1)  # Make first row of main frame stretch vertically

        
        self.appearance_mode_optionmenu.set("Dark")
        self.scaling_optionmenu.set("100%")
        self.create_options()

    def create_options(self):
        for i in range(10):
            button = customtkinter.CTkButton(self, text=f'number {i}', command=self.button_function)
            button.grid(row = i, column = 1)
            self.grid_rowconfigure(i, weight=1)
        
        '''self.computers()
        
    def open_new_window(self, ip):
        new_window = customtkinter.CTkToplevel(self)
        new_window.title(f"{ip}")
        new_window.geometry("300x200")

        #make the pop up window stay on top
        new_window.wm_attributes("-topmost", True)
        
        # Add your desired widgets to the new window
        label = customtkinter.CTkLabel(new_window, text=f"info on {ip}")
        label.pack(padx=20, pady=50)
        
    def computers(self):
        self.cursor.execute(f"SELECT * FROM {self.table_name};")
        computers = self.cursor.fetchall()
        col = 1
        row = 1
        for computer in computers:
            button = customtkinter.CTkButton(master=self, text=computer[0], command= lambda ip = computer[0]: self.open_new_window(ip), image=self.comp_icon)
            if computer[1] == 'off':
                button.configure(state="disabled")
            button.grid(row=row, column=col, padx=(20, 20), pady=(20, 20), sticky="nsew")
            if col >= 5:
                col = 1
                row += 1
            else:
                col += 1

        self.cursor.execute(f"SELECT ip_address FROM {self.table_name} WHERE connection_status='off';")
        off_comps = self.cursor.fetchall()
        print(off_comps)
        txt=1
        for computer in off_comps:
            
            button = customtkinter.CTkButton(master=self, state="disabled", text=txt, command=lambda: self.open_new_window(txt), image=self.comp_icon)
            button.grid(row=row, column=col, padx=(20, 20), pady=(20, 20), sticky="nsew")
            if col >= 5:
                col = 1
                row += 1
            else:
                col += 1
            txt+=1
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((1,2,3,4,5), weight=1)
        '''
        
    def change_theme(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)
    def change_scaling(self, new_scaling):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)
    def button_function(self):
        print('pressed')


if __name__ == '__main__':
    ServerGUI = ServerGUI()
    ServerGUI.mainloop()