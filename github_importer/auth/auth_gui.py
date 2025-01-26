import tkinter as tk
from tkinter import ttk

class AuthGUI:
    """GUI components for GitHub authorization."""

    def __init__(self, root, auth_manager, status_label):
        self.root = root
        self.auth_manager = auth_manager
        self.status_label = status_label

        auth_frame = ttk.LabelFrame(root, text="Authorization")
        auth_frame.pack(padx=20, pady=20, fill="x")

        auth_button = ttk.Button(auth_frame, text="Authorize with GitHub", command=self.authorize)
        auth_button.pack(pady=10)

    def authorize(self):
        """Handles the authorization button click."""
        self.status_label.config(text="Starting authorization process...", foreground="black")
        try:
            self.auth_manager.authorize_github()
            self.status_label.config(text="Authorization successful! (Token retrieved in background)", foreground="green")
        except Exception as e:
          self.status_label.config(text=f"Authorization failed: {e}", foreground="red")