from github_importer.config.config import Config
from github_importer.auth.auth_manager import AuthManager
from github_importer.auth.auth_gui import AuthGUI
from github_importer.github_api.github_client import GitHubClient
from github_importer.import_export.data_importer import DataImporter
from github_importer.import_export.import_gui import ImportGUI
from github_importer.gui.main_window import MainWindow
from github_importer.utils.logger import Logger


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
        root = MainWindow(None, None)
        auth_gui = AuthGUI(root.root, auth_manager, root.status_label)

        # Set the initial access token to the AuthManager, then set github_client and data_importer
        def set_token_and_client():
            access_token = auth_manager.get_access_token()
            if access_token:
                github_client = GitHubClient(access_token, logger)
                data_importer = DataImporter(github_client, logger)
                import_gui = ImportGUI(root.root, data_importer, root.status_label, root.repo_owner_entry[0],
                                       root.repo_owner_entry[1])
                root.import_gui = import_gui

        auth_manager.get_access_token = set_token_and_client  # Override the getter function for token
        root.auth_gui = auth_gui

        root.run()

    create_gui()


if __name__ == "__main__":
    main()