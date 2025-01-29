# github_importer/gui/main_window.py

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from typing import Optional, Dict, Any
from datetime import datetime

from github_importer.utils.logger import Logger
from github_importer.import_export.data_importer import DataImporter
from github_importer.github_api.github_client import GitHubClient
from github_importer.utils.token_storage import TokenStorage
from github_importer.auth.auth_manager import AuthManager
from github_importer.config.config import Config

from github_importer.gui.notification_manager import NotificationManager
from github_importer.gui.ui_elements import UIElements
from github_importer.gui.header_manager import HeaderManager
from github_importer.gui.navigation_manager import NavigationManager
from github_importer.gui.content_area_manager import ContentAreaManager
from github_importer.gui.import_section_manager import ImportSectionManager
from github_importer.gui.activity_log_manager import ActivityLogManager
from github_importer.gui.textbox_logger import TextboxLogger
from github_importer.gui.status_interface import StatusInterface
from github_importer.gui.activity_log_model import ActivityLogModel
from github_importer.gui.notification_model import NotificationModel
from github_importer.gui.custom_messagebox import CustomMessageBox


class MainWindow:
    """
    The main application window for the GitHub Milestones Importer.

    This class sets up the main GUI using customtkinter, following GitHub's
    design guidelines. It manages the overall structure and interactions between
    components and handles application-level actions.

    Attributes:
        root (ctk.CTk): The main application window
        logger (Logger): The application's logger instance
        github_client (GitHubClient): GitHub client for API interactions
        ui_elements (UIElements): Styling settings
        notification_manager (NotificationManager): Handles notifications
        status_interface (StatusInterface): Manages status updates
    """

    def __init__(self,
                 auth_gui: Optional['AuthGUI'],
                 github_client: Optional['GitHubClient'],
                 import_gui: Optional['ImportGUI'],
                 logger: Logger):
        """
        Initialize the main window with all necessary components.

        Args:
            auth_gui: Authentication GUI instance
            github_client: GitHub client instance
            import_gui: Import GUI instance
            logger: Logger instance
        """
        # Initialize core components
        self.logger = logger
        self.root = ctk.CTk()
        self.root.title("GitHub Milestones Importer")

        # Set up managers and clients
        self.auth_manager = AuthManager(Config(), logger)
        self.github_client = GitHubClient(
            TokenStorage().load_tokens()[0],
            logger,
            self.auth_manager
        )

        # Initialize models
        self.activity_log_model = ActivityLogModel()
        self.notification_model = NotificationModel()

        # Initialize UI components
        self.ui_elements = UIElements()
        self.notification_manager = NotificationManager(self.root, self.ui_elements)
        self.textbox_logger = TextboxLogger(self.ui_elements)
        self.status_interface = StatusInterface(self, self.notification_manager)

        # Set up activity log
        self.activity_log = ActivityLogManager(
            self.ui_elements,
            self.textbox_logger,
            self.root
        )

        # Initialize data importer
        self.data_importer = DataImporter(self.github_client, logger)
        self.data_importer.status_interface = self.status_interface

        # Set up import section with all callbacks
        self.import_section = ImportSectionManager(
            self.root,
            self.ui_elements,
            self.import_milestones,  # Import callback
            self.export_milestones,  # Export callback
            self.clear_milestones,  # Clear callback
            self.github_client,
            self.logger
        )

        # Set up navigation and header
        self.navigation = NavigationManager(
            self.root,
            self.ui_elements,
            self.update_repo_dropdown_command
        )

        self.header = HeaderManager(
            self.root,
            self.ui_elements,
            self.update_repo_dropdown_command
        )

        # Set up content area
        self.content_area = ContentAreaManager(
            self.root,
            self.ui_elements,
            self.import_section,
            self.activity_log
        )

        # Initialize events and state
        self.logger.addHandler(self.textbox_logger)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.repo_selection = self.header.repo_selector.repo_selection

        # Update initial state
        self.update_repo_dropdown()
        self.import_section.disable_buttons()  # Disable all buttons initially

    def update_repo_dropdown_command(self, selected_repo: str) -> None:
        """
        Handle repository selection changes.

        Args:
            selected_repo: The selected repository string
        """
        if selected_repo and self.validate_repository(selected_repo):
            self._enable_import_button()
            self.status_interface.update(
                f"Selected repository: {selected_repo}",
                'info'
            )
        else:
            self.status_interface.update(
                "Invalid repository selection",
                'error'
            )

    def validate_repository(self, repo_string: str) -> bool:
        """
        Validate repository string format.

        Args:
            repo_string: Repository string to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not repo_string:
            return False
        parts = repo_string.split('/')
        if len(parts) != 2:
            return False
        return all(part.strip() for part in parts)

    def update_repo_dropdown(self) -> None:
        """Update repository dropdown with available GitHub repositories."""
        try:
            repos = self.github_client.get_user_repos()
            repo_list = []

            for repo in repos:
                owner = repo['owner']['login']
                name = repo['name']
                icon = '󰒋' if repo['owner']['type'] == 'Organization' else '󰀄'
                repo_list.append(f"{icon} {owner}/{name}")

            self.header.repo_selector.repo_dropdown.configure(
                values=repo_list,
                state="normal",
                dropdown_fg_color=self.ui_elements.surface_color,
                dropdown_text_color=self.ui_elements.text_color,
                text_color=self.ui_elements.text_color
            )

            self.status_interface.update(
                f"Found {len(repo_list)} repositories",
                'info'
            )
        except Exception as e:
            self.status_interface.update(f"Failed to update repositories: {e}", 'error')

    def _enable_import_button(self) -> None:
        """Enable all buttons when repo is selected."""
        if self.repo_selection.get():
            self.import_section.enable_buttons()
        else:
            self.import_section.disable_buttons()

    def import_milestones(self) -> None:
        """Handle milestone import process."""
        try:
            selected_repo = self.repo_selection.get().split("/")
            if len(selected_repo) != 2:
                raise ValueError("Invalid repository format")

            user_name = selected_repo[0][2:].strip()  # Remove icon
            repo_name = selected_repo[1].strip()

            file_path = self.open_file_dialog()
            if file_path:
                self.status_interface.update(
                    f"Starting import from {file_path}",
                    'info'
                )
                self.data_importer.import_data(file_path, user_name, repo_name)
                self.status_interface.update(
                    "Import completed successfully",
                    'success'
                )
            else:
                self.status_interface.update(
                    "Import cancelled - no file selected",
                    'info'
                )

        except Exception as e:
            self.status_interface.update(f"Import failed: {e}", 'error')

    def export_milestones(self) -> None:
        """Handle milestone export process."""
        try:
            selected_repo = self.repo_selection.get().split("/")
            if len(selected_repo) != 2:
                raise ValueError("Invalid repository format")

            user_name = selected_repo[0][2:].strip()  # Remove icon
            repo_name = selected_repo[1].strip()

            # Get save location
            file_path = self.save_file_dialog(f"{user_name}_{repo_name}_milestones")
            if file_path:
                self.status_interface.update(
                    f"Starting export to {file_path}",
                    'info'
                )
                self.data_importer.export_milestones(user_name, repo_name, file_path)
            else:
                self.status_interface.update(
                    "Export cancelled - no file selected",
                    'info'
                )

        except Exception as e:
            self.status_interface.update(f"Export failed: {e}", 'error')

    # github_importer/gui/main_window.py

    from github_importer.gui.custom_messagebox import CustomMessageBox

    def clear_milestones(self) -> None:
        """Handle clearing all issues and milestones."""
        try:
            selected_repo = self.repo_selection.get().split("/")
            if len(selected_repo) != 2:
                raise ValueError("Invalid repository format")

            user_name = selected_repo[0][2:].strip()  # Remove icon
            repo_name = selected_repo[1].strip()

            # Show confirmation dialog
            msg = CustomMessageBox(
                master=self.root,
                title="Confirm Clear",
                message=f"Are you sure you want to clear ALL issues and milestones from {user_name}/{repo_name}?\n\nThis action cannot be undone!",
                option_1="Cancel",
                option_2="Clear All",
                button_color=self.ui_elements.error_color,
                button_hover_color="#FF6B6B",
                cancel_button_color=self.ui_elements.secondary_color
            )

            if msg.get() == "OK":  # "OK" is returned when "Clear All" is clicked
                self.status_interface.update(
                    f"Starting to clear all issues and milestones from {user_name}/{repo_name}...",
                    'info'
                )

                # Perform the clear operation
                self.data_importer.clear_all_milestones_and_issues(user_name, repo_name)

                self.status_interface.update(
                    "Successfully cleared all issues and milestones",
                    'success'
                )
            else:
                self.status_interface.update(
                    "Clear operation cancelled",
                    'info'
                )

        except Exception as e:
            self.status_interface.update(f"Failed to clear issues and milestones: {e}", 'error')

    def open_file_dialog(self) -> Optional[str]:
        """
        Open file dialog for selecting import file.

        Returns:
            Optional[str]: Selected file path or None if cancelled
        """
        root = tk.Tk()
        root.withdraw()
        try:
            return filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")],
                title="Select a JSON file to import",
                initialdir="/"  # Start from root directory
            )
        finally:
            root.destroy()

    def save_file_dialog(self, default_name: str) -> Optional[str]:
        """
        Open file dialog for saving export file.

        Args:
            default_name: Default filename

        Returns:
            Optional[str]: Selected file path or None if cancelled
        """
        root = tk.Tk()
        root.withdraw()
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"{default_name}_{timestamp}.json"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                title="Save Export As",
                initialfile=default_filename,
                initialdir="/"  # Start from root directory
            )
            return file_path if file_path else None
        finally:
            root.destroy()

    def cleanup(self) -> None:
        """Clean up resources before closing."""
        self.logger.removeHandler(self.textbox_logger)
        # Clean up other resources as needed

    def on_close(self) -> None:
        """Handle application closure."""
        msg = CustomMessageBox(
            master=self.root,
            title="Close GitHub Milestones Importer",
            message="Are you sure you want to close the importer?",
            option_1="Cancel",
            option_2="Close",
            button_color=self.ui_elements.primary_color,
            cancel_button_color=self.ui_elements.secondary_color
        )

        if msg.get() == "OK":  # "OK" is returned when "Close" is clicked
            self.logger.info("Closing GitHub Milestones Importer")
            self.cleanup()
            self.root.destroy()

    def get_state(self) -> Dict[str, Any]:
        """
        Get current application state for testing.

        Returns:
            dict: Current state information
        """
        return {
            'selected_repo': self.repo_selection.get(),
            'import_button_enabled': self.import_section.import_button.button.cget('state') == 'normal',
            'export_button_enabled': self.import_section.export_button.button.cget('state') == 'normal',
            'clear_button_enabled': self.import_section.clear_button.button.cget('state') == 'normal',
            'notification_count': len(self.notification_manager.items)
        }

    def run(self) -> None:
        """Initialize and run the main application window."""
        # Center window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = 800
        window_height = 600

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.mainloop()