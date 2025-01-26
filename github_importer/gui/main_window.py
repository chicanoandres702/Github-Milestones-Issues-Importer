import tkinter as tk
from tkinter import ttk
from github_importer.utils.logger import Logger

class MainWindow:
    def __init__(self, auth_gui, github_client, import_gui, logger):
        self.root = tk.Tk()
        self.root.title("GitHub Milestones Importer")
        self.logger = logger
        self.github_client = github_client
        self.auth_gui = auth_gui
        self.import_gui = import_gui

        self.status_label = ttk.Label(self.root, text="Ready")
        self.status_label.pack(pady=10)

        self.repo_label = ttk.Label(self.root, text="Select Repository:")
        self.repo_label.pack()
        self.repo_selection = ttk.Combobox(self.root, values=[])
        self.repo_selection.pack(pady=10)

    def update_repo_dropdown(self):
        if self.github_client:
            try:
                 repos = self.github_client.get_user_repos()
                 repo_list = [f"{repo['owner']['login']}/{repo['name']}" for repo in repos]
                 self.repo_selection['values'] = repo_list
                 self.logger.info(f"Repos updated in dropdown: {repo_list}")
            except Exception as e:
                self.logger.error(f"An error has occurred retreiving user repos: {e}")

    def run(self):
        self.root.mainloop()