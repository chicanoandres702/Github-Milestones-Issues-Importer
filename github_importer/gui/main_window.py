import tkinter as tk
from tkinter import ttk

class MainWindow:
    """Sets up and manages the main application window."""

    def __init__(self, auth_gui, import_gui):
        self.root = tk.Tk()
        self.root.title("GitHub Import Tool")
        self.status_label = ttk.Label(self.root, text="")
        self.status_label.pack()
        self.repo_owner_entry = self._create_repo_frame()
        self.auth_gui = auth_gui
        self.import_gui = import_gui

    def _create_repo_frame(self):
        """Creates the repository information frame."""
        repo_frame = ttk.LabelFrame(self.root, text="Repository Information")
        repo_frame.pack(padx=20, pady=10, fill="x")

        repo_owner_label = ttk.Label(repo_frame, text="Repository Owner:")
        repo_owner_label.grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        repo_owner_entry = ttk.Entry(repo_frame)
        repo_owner_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        repo_name_label = ttk.Label(repo_frame, text="Repository Name:")
        repo_name_label.grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        repo_name_entry = ttk.Entry(repo_frame)
        repo_name_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        return repo_owner_entry, repo_name_entry

    def run(self):
      """Starts the main GUI loop."""
      self.root.mainloop()