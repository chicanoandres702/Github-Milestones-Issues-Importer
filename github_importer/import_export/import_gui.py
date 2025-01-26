import tkinter as tk
from tkinter import ttk, filedialog


class ImportGUI:
    """GUI components for importing data."""

    def __init__(self, root, data_importer, status_label, repo_owner_entry, repo_name_entry):
        self.root = root
        self.data_importer = data_importer
        self.status_label = status_label
        self.repo_owner_entry = repo_owner_entry
        self.repo_name_entry = repo_name_entry
        self.import_file_entry = None  # Added to make it accessible in `browse_file` method

        import_file_frame = ttk.LabelFrame(root, text="Import File")
        import_file_frame.pack(padx=20, pady=10, fill="x")

        import_file_label = ttk.Label(import_file_frame, text="Import File:")
        import_file_label.grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)

        self.import_file_entry = ttk.Entry(import_file_frame)
        self.import_file_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        import_file_button = ttk.Button(import_file_frame, text="Browse", command=self.browse_file)
        import_file_button.grid(row=0, column=2, padx=5, pady=5)

        import_button = ttk.Button(root, text="Import Data", command=self.import_data)
        import_button.pack(pady=10)

    def browse_file(self):
        """Opens a file dialog to select the JSON file."""
        filepath = filedialog.askopenfilename(
            initialdir="/",
            title="Select file",
            filetypes=(("JSON files", "*.json"), ("all files", "*.*"))
        )
        self.import_file_entry.delete(0, tk.END)
        self.import_file_entry.insert(0, filepath)

    def import_data(self):
        """Handles the import data button click."""
        self.status_label.config(text="Starting import process...", foreground="black")
        repo_owner = self.repo_owner_entry.get()
        repo_name = self.repo_name_entry.get()
        import_file = self.import_file_entry.get()
        try:
            if not all([repo_owner, repo_name, import_file]):
                self.status_label.config(text="Error: Please provide all repo information and import file!",
                                         foreground="red")
                return
            if self.data_importer.import_data(repo_owner, repo_name, import_file):
                self.status_label.config(text="Import successful!", foreground="green")
            else:
                self.status_label.config(text="Import failed (see log for more info)", foreground="red")
        except Exception as e:
            self.status_label.config(text=f"An error occurred: {e}", foreground="red")