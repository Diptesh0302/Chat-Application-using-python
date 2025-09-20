# client.py
import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext

class ChatClient:
    def __init__(self, master):
        # --- Window Setup ---
        master.withdraw() # Hide the root window
        self.HOST = simpledialog.askstring("Server IP", "Enter server IP address:", parent=master)
        if not self.HOST: exit()
        self.PORT = 8500
        self.nickname = simpledialog.askstring("Nickname", "Choose your nickname:", parent=master)
        if not self.nickname: exit()
        master.deiconify() # Show the root window again

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((self.HOST, self.PORT))
        except Exception as e:
            print(f"Error connecting to server: {e}")
            master.destroy()
            return

        # --- GUI Elements ---
        self.master = master
        master.title(f"Chat - {self.nickname}")
        master.configure(bg="#2c2f33")

        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, state='disabled', bg="#23272a", fg="#ffffff", font=("Helvetica", 12))
        self.text_area.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)

        self.msg_entry = tk.Entry(master, bg="#40444b", fg="#ffffff", font=("Helvetica", 12), insertbackground='white')
        self.msg_entry.pack(padx=20, pady=5, fill=tk.X, expand=False)
        self.msg_entry.bind("<Return>", self.write_message)

        self.send_button = tk.Button(master, text="Send", command=self.write_message, bg="#7289da", fg="white", font=("Helvetica", 10, "bold"), relief=tk.FLAT)
        self.send_button.pack(padx=20, pady=5)
        
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- Start Threads ---
        self.gui_done = False
        receive_thread = threading.Thread(target=self.receive_message)
        receive_thread.daemon = True # a daemon thread exits when the main thread exits
        receive_thread.start()

    def receive_message(self):
        """ Listens for messages from the server. """
        while not self.gui_done:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self.client.send(self.nickname.encode('utf-8'))
                elif message:
                    self.text_area.config(state='normal')
                    self.text_area.insert('end', message + '\n')
                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')
            except:
                print("An error occurred!")
                self.client.close()
                break
    
    def write_message(self, event=None):
        """ Sends a message to the server. """
        message_text = self.msg_entry.get()
        if message_text:
            message = f'{self.nickname}: {message_text}'
            try:
                self.client.send(message.encode('utf-8'))
                self.msg_entry.delete(0, 'end')
            except:
                print("Could not send message.")

    def on_closing(self):
        """ Handles window closing event. """
        self.gui_done = True
        self.client.close()
        self.master.destroy()

# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    client_app = ChatClient(root)
    root.mainloop()

