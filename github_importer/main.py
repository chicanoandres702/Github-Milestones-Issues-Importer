# github_importer/main.py
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


class Application:
    def __init__(self):
        self.logger = Logger("github_importer")
        self.config = Config()
        self.auth_manager = None
        self.github_client = None
        self.data_importer = None
        self.root = None
        self.auth_gui = None
        self.setup_completed = False

        self.logger.info(f"Configuration loaded: {self.config}")

        # Initialize main window first
        self.root = MainWindow(None, None, None, self.logger)

        # Disable repo dropdown initially
        self.root.header.repo_selector.repo_dropdown.configure(state="disabled")

        # Setup auth manager
        self.auth_manager = AuthManager(self.config, self.logger)

        # Setup auth GUI
        self.auth_gui = AuthGUI(
            self.root.root,
            self.auth_manager,
            self.root.status_interface
        )
        self.root.auth_gui = self.auth_gui

    def setup_after_auth(self, access_token):
        """Setup application after successful authentication"""
        if self.setup_completed:
            return

        try:
            # Setup GitHub client
            self.github_client = GitHubClient(access_token, self.logger, self.auth_manager)

            # Authenticate with the GitHub API
            if self.github_client.authenticate():
                self.setup_completed = True
                self.logger.info(f"Access token retrieved: {access_token}")
                self.logger.info(f"Github Client set: {self.github_client}")

                # Setup data importer
                self.data_importer = DataImporter(self.github_client, self.logger)

                # Setup Import GUI
                import_gui = ImportGUI(
                    self.root.root,
                    self.data_importer,
                    self.github_client,
                    self.logger,
                    self.root.status_interface,
                    self.root.repo_selection
                )

                self.root.github_client = self.github_client
                self.root.import_gui = import_gui

                # Enable and update repo dropdown
                self.root.header.repo_selector.repo_dropdown.configure(state="normal")
                self.root.update_repo_dropdown()

                # Get user info
                try:
                    url = "https://api.github.com/user"
                    headers = {
                        "Authorization": f"token {access_token}",
                        "Accept": "application/vnd.github.v3+json"
                    }
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    self.logger.info(f"Successfully retrieved User info: {data}")
                    self.root.status_interface.update(
                        f"Logged in as {data['login']}",
                        'success'
                    )
                except Exception as e:
                    self.logger.error(f"An error has occurred getting user info: {e}")

                return True
            else:
                self.logger.error("Failed to authenticate with GitHub API.")
                self.root.status_interface.update(
                    "Authentication failed. Please try again.",
                    'error'
                )
                return False

        except Exception as e:
            self.logger.error(f"Error in setup_after_auth: {e}")
            self.root.status_interface.update(
                f"Setup error: {str(e)}",
                'error'
            )
            return False

    def run(self):
        """Run the application"""
        try:
            # Check for stored token
            self.auth_manager.load_stored_tokens()
            old_token = self.auth_manager.access_token

            if old_token:
                self.logger.info("Found stored token, attempting to refresh")
                if self.auth_manager.refresh_access_token():
                    self.logger.info("Successfully refreshed token")
                    if self.setup_after_auth(self.auth_manager.access_token):
                        self.root.status_interface.update(
                            "Successfully authenticated with GitHub",
                            'success'
                        )
                else:
                    self.logger.error("Token refresh failed, starting new auth flow")
                    self.root.status_interface.update(
                        "Token expired, please log in again",
                        'info'
                    )
                    self.auth_manager.set_on_auth_success(self.setup_after_auth)
                    self.auth_manager.start_oauth_flow()
            else:
                self.logger.info("No stored token found, starting auth flow")
                self.root.status_interface.update(
                    "Please log in to GitHub",
                    'info'
                )
                self.auth_manager.set_on_auth_success(self.setup_after_auth)
                self.auth_manager.start_oauth_flow()

            # Start the main event loop
            self.root.run()

        except Exception as e:
            self.logger.error(f"Error in run: {e}")
            raise


def main():
    """Main entry point for the application"""
    try:
        app = Application()
        app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()