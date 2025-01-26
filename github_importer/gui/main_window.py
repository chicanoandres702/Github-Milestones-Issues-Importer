import tkinter as tk
from tkinter import ttk


class MainWindow:
    """Sets up and manages the main application window."""

    def __init__(self, auth_gui, import_gui, github_client, logger):
        self.root = tk.Tk()
        self.root.title("GitHub Import Tool")
        self.status_label = ttk.Label(self.root, text="")
        self.status_label.pack()
        self.auth_gui = auth_gui
        self.import_gui = import_gui
        self.github_client = github_client
        self.logger = logger
        self.repo_selection = self._create_repo_dropdown()

    def _create_repo_dropdown(self):
        """Creates the repository dropdown menu."""

        repo_frame = ttk.LabelFrame(self.root, text="Repository Information")
        repo_frame.pack(padx=20, pady=10, fill="x")

        repo_label = ttk.Label(repo_frame, text="Select Repository:")
        repo_label.pack(pady=5)
        self.repo_dropdown = ttk.Combobox(repo_frame, state="readonly")
        self.repo_dropdown.pack()
        return self.repo_dropdown

    def update_repo_dropdown(self):
        try:
            repos_data = self.github_client.get_user_repositories()
            self.logger.info(f"Repos data: {repos_data}")
            if repos_data:
                self.repo_list = [f"{repo['owner']['login']}/{repo['name']}" for repo in repos_data]
                self.logger.info(f"Repo list: {self.repo_list}")
                self.repo_dropdown["values"] = self.repo_list
                self.logger.info(f"Found {len(self.repo_list)} repos to display in dropdown menu")
                self.status_label.config(text="Loaded repository list", foreground="green")
            else:
                self.logger.error("Unable to load list of repositories")
                self.status_label.config(text="Unable to load list of repositories", foreground="red")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred in updating dropdown menu: {e} - {e}")
            self.status_label.config(text=f"An unexpected error occurred in updating dropdown menu: {e}",
                                     foreground="red")

    def run(self):
        """Starts the main GUI loop."""
        self.root.mainloop()