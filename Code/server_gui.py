import customtkinter
import tkinter
import server

class server_gui:
    
    def __init__(self):
        self.server = 
        customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

        self.app = customtkinter.CTk()  # create CTk window like you do with the Tk window
        self.app.geometry("1200x800")
        
        self.app.mainloop()