import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime


class ImportGUI:
    def __init__(self, root, data_importer, github_client, logger, status_label, repo_dropdown):
        self.root = root
        self.data_importer = data_importer
        self.logger = logger
        self.status_label = status_label
        self.repo_dropdown = repo_dropdown
        self.github_client = github_client
        self.import_file_path = None

        # UI elements
        self.import_button = ttk.Button(self.root, text="Import Milestones", command=self.open_file_dialog)
        self.import_button.pack(pady=10)

        self.export_button = ttk.Button(self.root, text="Export Milestones", command=self.export_milestones)
        self.export_button.pack(pady=10)

        self.clear_button = ttk.Button(self.root, text="Clear Issues/Milestones", command=self.clear_milestones_and_issues)
        self.clear_button.pack(pady=10)

    def clear_milestones_and_issues(self):
      repo_string = self.repo_dropdown.get()
      repo_string = repo_string.strip() #remove white space

      if not repo_string:
           messagebox.showerror("Error", "Please select a repository.")
           return

      if "/" not in repo_string:
            messagebox.showerror("Error", "Invalid format for repository. Must be owner/repo.")
            return
      try:
          repo_owner, repo_name = repo_string.split("/")
      except ValueError as e:
            messagebox.showerror("Error",f"An error has occurred processing the selected repository: {e}")
            return

      if messagebox.askokcancel("Confirm Clear", "Are you sure you want to delete all milestones and issues in the repository?"):
        try:
           self.update_status("Clearing milestones and issues...")
           self.data_importer.clear_all_milestones_and_issues(repo_owner, repo_name)
           self.update_status("Milestones and issues cleared successfully!")

        except Exception as e:
            self.update_status(f"Error clearing milestones and issues: {e}")
            self.logger.error(f"Error clearing milestones and issues: {e}")
            messagebox.showerror("Error", f"An error has occurred clearing issues and milestones: {e}")


    def open_file_dialog(self):
        self.import_file_path = filedialog.askopenfilename(title="Select Milestone File", filetypes=(("JSON files", "*.json"), ("all files", "*.*")))
        if not self.import_file_path:
           return
        self.import_milestones()

    def import_milestones(self):
        if not self.import_file_path:
            return
        repo_string = self.repo_dropdown.get()
        repo_string = repo_string.strip() #remove white space
        if not repo_string:
            messagebox.showerror("Error", "Please select a repository.")
            return

        if "/" not in repo_string:
            messagebox.showerror("Error", "Invalid format for repository. Must be owner/repo.")
            return

        try:
            repo_owner, repo_name = repo_string.split("/")
        except ValueError as e:
            messagebox.showerror("Error",f"An error has occurred processing the selected repository: {e}")
            return
        start_time = datetime.now()
        self.update_status("Importing milestones...")
        try:
            self.data_importer.import_milestones(self.import_file_path, repo_owner, repo_name)
            end_time = datetime.now()
            self.update_status(f"Milestones imported successfully in {end_time - start_time}!")
        except Exception as e:
            self.update_status(f"Error importing milestones: {e}")
            self.logger.error(f"Error importing milestones: {e}")
            messagebox.showerror("Error", f"An error has occurred importing milestones: {e}")

    def export_milestones(self):
        repo_string = self.repo_dropdown.get()
        repo_string = repo_string.strip() #remove white space
        if not repo_string:
             messagebox.showerror("Error", "Please select a repository.")
             return

        if "/" not in repo_string:
            messagebox.showerror("Error", "Invalid format for repository. Must be owner/repo.")
            return

        try:
            repo_owner, repo_name = repo_string.split("/")
        except ValueError as e:
            messagebox.showerror("Error",f"An error has occurred processing the selected repository: {e}")
            return

        start_time = datetime.now()
        self.update_status("Exporting milestones...")
        try:
            self.data_importer.export_milestones(repo_owner, repo_name)
            end_time = datetime.now()
            self.update_status(f"Milestones exported successfully in {end_time - start_time}!")
        except Exception as e:
            self.update_status(f"Error exporting milestones: {e}")
            self.logger.error(f"Error exporting milestones: {e}")
            messagebox.showerror("Error", f"An error has occurred exporting milestones: {e}")

    def update_status(self, message):
        self.status_label.config(text=message)
        self.status_label.update()