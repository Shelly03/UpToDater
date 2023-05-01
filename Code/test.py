import sqlite3
import customtkinter
import tkinter
from PIL import Image,ImageTk
import os

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
        
class ServerGUI(customtkinter.CTk):
    
    def __init__(self, db_name='ipconections.db'):
        super().__init__()
        
        self.title('PROJECT NAME')
        self.geometry(f"{1100}x{580}")

        #db setup
        self.db_name = db_name
        self.table_name = 'ipAddresses'
        #new conn and corsur
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        #create the table is it is not there
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self.table_name}
                            (ip_address text, connection_status text)''')
        self.conn.commit()
        
        #images
        self.comp_icon=customtkinter.CTkImage(Image.open(r"Code\sources\computer_icon.png"))
                
        # sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        # project name
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="project name", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        #change theme
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="theme:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_theme)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        
        #add scaling
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],command=self.change_scaling)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.cursor.execute(f"update {self.table_name} set connection_status = 'off' where ip_address = '127.0.0.1'")
        self.computers()
        
    def open_new_window(self, ip):
        new_window = customtkinter.CTkToplevel(self)
        new_window.title(f"{ip}")
        new_window.geometry("300x200")

        # Add your desired widgets to the new window
        label = customtkinter.CTkLabel(new_window, text=f"info on {ip}")
        label.pack(padx=20, pady=50)
        
    def computers(self):
        self.cursor.execute(f"SELECT ip_address FROM {self.table_name} WHERE connection_status='on';")
        on_comps = self.cursor.fetchall()
        col = 1
        row = 1
        txt=1
        for computer in on_comps:
            
            button = customtkinter.CTkButton(master=self, text=txt, command=lambda: self.open_new_window(txt), image=self.comp_icon)
            button.grid(row=row, column=col, padx=(20, 20), pady=(20, 20), sticky="nsew")
            if col >= 5:
                col = 1
                row += 1
            else:
                col += 1
            txt+=1

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
        
        
    def change_theme(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)
    def change_scaling(self, new_scaling):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)
    def button_function(self):
        print('pressed')

if __name__ == '__main__':
    app = ServerGUI()
    app.mainloop()