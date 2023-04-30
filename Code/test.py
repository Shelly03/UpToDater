import sqlite3
import customtkinter
import tkinter

class ServerGUI:
    def __init__(self, db_name='ipconections.db'):
        # Create the parent frame and add a canvas widget to it
        self.app = customtkinter.CTk()  # create CTk window like you do with the Tk window
        self.app.geometry("1000x600")

        customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")

        self.app.title('UpToDater')
        self.db_name = db_name

        # Create a new database connection and cursor
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

        # Create the clients table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS clients
                            (ip_address text UNIQUE, connection_status text)''')
        self.conn.commit()

        
        button = customtkinter.CTkButton(master=self.app, text="CTkButton", command=self.button_function, image='C:\\Users\\shelly ben zion\\Desktop\\Cyber project\\UpToDater\\Code\\sources\\computer_icon.png')
        button.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        self.app.mainloop()

    def button_function(self):
        print('pressed')

if __name__ == '__main__':
    app = ServerGUI()
    app.mainloop()