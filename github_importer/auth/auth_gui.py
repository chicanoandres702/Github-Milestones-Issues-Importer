import tkinter as tk
from tkinter import ttk
class AuthGUI:
    def __init__(self, root, auth_manager, status_label):
        self.root = root
        self.auth_manager = auth_manager
        self.status_label = status_label
        self.auth_button = ttk.Button(self.root, text="Authorize with GitHub", command=self.start_auth)
        self.auth_button.pack(pady=10)

    def start_auth(self):
        self.update_status("Authorizing...")
        self.auth_manager.start_oauth_flow()
    def update_status(self, message):
       self.status_label.config(text=message)
       self.status_label.update()