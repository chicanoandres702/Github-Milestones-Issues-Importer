from github_importer.config.config import Config
from github_importer.auth.auth_manager import AuthManager
from github_importer.auth.auth_gui import AuthGUI
from github_importer.github_api.github_client import GitHubClient
from github_importer.import_export.data_importer import DataImporter
from github_importer.import_export.import_gui import ImportGUI
from github_importer.gui.main_window import MainWindow
from github_importer.utils.logger import Logger
import requests


def main():
    # --- Setup ---
    logger = Logger("github_importer")
    config = Config()
    logger.info(f"Configuration loaded: {config}")

    auth_manager = AuthManager(config, logger)
    github_client = None  # Access token will be set after authentication
    data_importer = None

    # --- GUI Setup ---
    root = None

    def create_gui():
        nonlocal root, github_client, data_importer
        root = MainWindow(None, None, None, logger)
        auth_gui = AuthGUI(root.root, auth_manager, root.status_label)

        # Set the initial access token to the AuthManager, then set github_client and data_importer
        def set_token_and_client(access_token):
            if not hasattr(set_token_and_client, 'called'):
                logger.info("Setting access token")
                set_token_and_client.called = True
                logger.info(f"Access token retrieved: {access_token}")
                github_client = GitHubClient(access_token, logger)
                logger.info(f"Github Client set: {github_client}")
                data_importer = DataImporter(github_client, logger)
                import_gui = ImportGUI(root.root, data_importer, root.status_label, root.repo_selection,
                                       root.repo_selection)  # Added root.repo_selection
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
                    logger.info(f"Successfully retrived User info: {data}")
                except Exception as e:
                    logger.error(f"An error has occurred getting user info: {e}")

                root.update_repo_dropdown()

        auth_manager.set_on_auth_success(set_token_and_client)  # pass in the function directly

        root.auth_gui = auth_gui

        root.run()

    create_gui()


if __name__ == "__main__":
    main()