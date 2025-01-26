# In `github_importer/main.py`
from github_importer.config.config import Config
from github_importer.auth.auth_manager import AuthManager
from github_importer.auth.auth_gui import AuthGUI
from github_importer.github_api.github_client import GitHubClient
from github_importer.import_export.data_importer import DataImporter
from github_importer.import_export.import_gui import ImportGUI
from github_importer.gui.main_window import MainWindow
from github_importer.utils.logger import Logger
import requests
from tkinter import messagebox

def main():
    # --- Setup ---
    logger = Logger("github_importer")
    config = Config()
    logger.info(f"Configuration loaded: {config}")

    auth_manager = AuthManager(config, logger)
    github_client = None
    data_importer = None

    # --- GUI Setup ---
    root = MainWindow(None, None, None, logger)
    auth_gui = AuthGUI(root.root, auth_manager, root.status_label)
    root.auth_gui = auth_gui

    def setup_after_auth(access_token):
        nonlocal github_client, data_importer, root

        github_client = GitHubClient(access_token, logger, auth_manager)
        status_code = github_client.check_access_token()
        if 200 <= status_code <= 299:
            logger.info(f"Access token retrieved: {access_token}")
            logger.info(f"Github Client set: {github_client}")
            data_importer = DataImporter(github_client, logger)
            import_gui = ImportGUI(root.root, data_importer, github_client, logger, root.status_label, root.repo_selection)
            root.github_client = github_client
            root.import_gui = import_gui
            url = "https://api.github.com/user"
            headers = {
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Successfully retrieved User info: {data}")
            except Exception as e:
                logger.error(f"An error has occurred getting user info: {e}")

            root.update_repo_dropdown()
            root.run()  # Start the Tkinter main loop

        else:
            logger.error(f"Invalid Access Token: Status code: {status_code}")
            messagebox.showerror("Error", "Invalid access token. Please try again.")

    def set_token_and_client(access_token):
        if not hasattr(set_token_and_client, 'called'):
            logger.info("Setting access token")
            set_token_and_client.called = True
            setup_after_auth(access_token)

    auth_manager.set_on_auth_success(set_token_and_client)

    # Check for old token and refresh if necessary
    auth_manager.load_stored_tokens()
    old_token = auth_manager.access_token
    if old_token:
        logger.info("Found old token, attempting to refresh it.")
        if auth_manager.refresh_access_token():
            logger.info("Successfully refreshed token.")
            set_token_and_client(auth_manager.access_token)
        else:
            logger.error("Failed to refresh token. Please login again.")
            root.run()
    else:
        logger.error("No old token found. Please login.")
        root.run()

if __name__ == "__main__":
    main()