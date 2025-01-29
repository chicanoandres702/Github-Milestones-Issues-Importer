# github_importer/gui/import_section_manager.py

import customtkinter as ctk
from typing import Callable
from github_importer.utils.logger import Logger
from github_importer.github_api.github_client import GitHubClient
from github_importer.gui.ui_elements import UIElements


class ImportHeaderItem:
    """
    Creates the import section header.

    Attributes:
        root (ctk.CTk): The main window
        ui_elements (UIElements): UI styling settings
    """

    def __init__(self):
        self.root = None
        self.ui_elements = None

    def create_header(self, parent: ctk.CTkFrame) -> None:
        """
        Create header with GitHub styling.

        Args:
            parent: Parent frame to contain the header
        """
        header_frame = ctk.CTkFrame(
            parent,
            fg_color=self.ui_elements.secondary_color,
            height=40,
            corner_radius=6
        )
        header_frame.pack(fill="x")

        header_label = ctk.CTkLabel(
            header_frame,
            text="󰍉 Import/Export Management",
            text_color=self.ui_elements.text_color,
            font=("Segoe UI", 14, "bold")
        )
        header_label.pack(side="left", padx=16, pady=8)


class ActionButtonItem:
    """
    Creates and manages action buttons.

    Attributes:
        ui_elements (UIElements): UI styling settings
        callback (Callable): Button click callback
        button (ctk.CTkButton): The button instance
        github_client (GitHubClient): GitHub client instance
        logger (Logger): Logger instance
    """

    def __init__(self,
                 ui_elements: UIElements,
                 callback: Callable,
                 github_client: GitHubClient,
                 logger: Logger):
        """
        Initialize action button.

        Args:
            ui_elements: UI styling settings
            callback: Button click callback
            github_client: GitHub client instance
            logger: Logger instance
        """
        self.root = None
        self.ui_elements = ui_elements
        self.callback = callback
        self.button = None
        self.github_client = github_client
        self.logger = logger

    def create_button(self, parent: ctk.CTkFrame, text: str, is_primary: bool = True) -> ctk.CTkButton:
        """
        Create a button with GitHub styling.

        Args:
            parent: Parent frame to contain the button
            text: Button text
            is_primary: Whether this is a primary button (affects styling)

        Returns:
            ctk.CTkButton: Created button instance
        """
        self.button = ctk.CTkButton(
            parent,
            text=text,
            command=self.callback,
            fg_color=self.ui_elements.primary_color if is_primary else self.ui_elements.secondary_color,
            hover_color=self.ui_elements.primary_hover_color if is_primary else self.ui_elements.secondary_hover_color,
            text_color="#FFFFFF",
            font=("Segoe UI", 12),
            height=32,
            corner_radius=6
        )
        return self.button

    def configure(self, **kwargs) -> None:
        """
        Configure button properties.

        Args:
            **kwargs: Button configuration parameters
        """
        if self.button:
            self.button.configure(**kwargs)


class ImportSectionManager:
    """
    Manages the import/export section of the application.

    This class coordinates the import header and action buttons,
    providing a complete interface for importing, exporting, and clearing milestones.

    Attributes:
        ui_elements (UIElements): UI styling settings
        import_header (ImportHeaderItem): Header manager
        import_button (ActionButtonItem): Import button manager
        export_button (ActionButtonItem): Export button manager
        clear_button (ActionButtonItem): Clear button manager
        root (ctk.CTk): The main window
    """

    def __init__(self,
                 root: ctk.CTk,
                 ui_elements: UIElements,
                 import_callback: Callable,
                 export_callback: Callable,
                 clear_callback: Callable,
                 github_client: GitHubClient,
                 logger: Logger):
        """
        Initialize the import section manager.

        Args:
            root: Main window instance
            ui_elements: UI styling settings
            import_callback: Import button callback
            export_callback: Export button callback
            clear_callback: Clear button callback
            github_client: GitHub client instance
            logger: Logger instance
        """
        self.ui_elements = ui_elements
        self.import_header = ImportHeaderItem()
        self.import_button = ActionButtonItem(
            ui_elements,
            import_callback,
            github_client,
            logger
        )
        self.export_button = ActionButtonItem(
            ui_elements,
            export_callback,
            github_client,
            logger
        )
        self.clear_button = ActionButtonItem(
            ui_elements,
            clear_callback,
            github_client,
            logger
        )
        self.root = root

    def create_import_section(self, parent: ctk.CTkFrame) -> None:
        """
        Create the complete import/export section with GitHub styling.

        Args:
            parent: Parent frame to contain the section
        """
        # Main frame
        import_frame = ctk.CTkFrame(
            parent,
            fg_color=self.ui_elements.surface_color,
            corner_radius=6
        )
        import_frame.pack(fill="x", pady=(0, 16))

        # Import Header
        self.import_header.root = self.root
        self.import_header.ui_elements = self.ui_elements
        self.import_header.create_header(import_frame)

        # Button container frame
        button_frame = ctk.CTkFrame(
            import_frame,
            fg_color="transparent"
        )
        button_frame.pack(fill="x", padx=16, pady=16)

        # Import Button
        import_btn = self.import_button.create_button(
            button_frame,
            "Import Issues/Milestones",
            is_primary=True
        )
        import_btn.pack(side="left", padx=(0, 8))

        # Export Button
        export_btn = self.export_button.create_button(
            button_frame,
            "Export Issues/Milestones",
            is_primary=False
        )
        export_btn.pack(side="left", padx=(0, 8))

        # Clear Button (with warning color)
        clear_btn = self.clear_button.create_button(
            button_frame,
            "Clear All Issues/Milestones",
            is_primary=False
        )
        clear_btn.configure(
            fg_color=self.ui_elements.error_color,
            hover_color="#FF6B6B"  # Lighter red for hover
        )
        clear_btn.pack(side="left")

    def enable_buttons(self) -> None:
        """Enable all buttons with appropriate styling."""
        self.import_button.configure(
            state="normal",
            fg_color=self.ui_elements.primary_color,
            hover_color=self.ui_elements.primary_hover_color,
            text="Import Issues/Milestones"
        )
        self.export_button.configure(
            state="normal",
            fg_color=self.ui_elements.secondary_color,
            hover_color=self.ui_elements.secondary_hover_color,
            text="Export Issues/Milestones"
        )
        self.clear_button.configure(
            state="normal",
            fg_color=self.ui_elements.error_color,
            hover_color="#FF6B6B",
            text="Clear All Issues/Milestones"
        )

    def disable_buttons(self) -> None:
        """Disable all buttons with appropriate styling."""
        self.import_button.configure(
            state="disabled",
            fg_color=self.ui_elements.secondary_color,
            hover_color=self.ui_elements.secondary_hover_color,
            text="Select a repository"
        )
        self.export_button.configure(
            state="disabled",
            fg_color=self.ui_elements.secondary_color,
            hover_color=self.ui_elements.secondary_hover_color,
            text="Select a repository"
        )
        self.clear_button.configure(
            state="disabled",
            fg_color=self.ui_elements.secondary_color,
            hover_color=self.ui_elements.secondary_hover_color,
            text="Select a repository"
        )

    def get_button_states(self) -> dict:
        """
        Get current button states.

        Returns:
            dict: Dictionary containing button states
        """
        return {
            'import_enabled': self.import_button.button.cget('state') == 'normal',
            'export_enabled': self.export_button.button.cget('state') == 'normal',
            'clear_enabled': self.clear_button.button.cget('state') == 'normal'
        }

    def update_button_states(self, is_repo_selected: bool) -> None:
        """
        Update button states based on repository selection.

        Args:
            is_repo_selected: Whether a repository is currently selected
        """
        if is_repo_selected:
            self.enable_buttons()
        else:
            self.disable_buttons()