# github_importer/gui/content_area_manager.py

import customtkinter as ctk
from typing import Optional
from github_importer.gui.ui_elements import UIElements
from github_importer.gui.import_section_manager import ImportSectionManager
from github_importer.gui.activity_log_manager import ActivityLogManager


class TabBarManager:
    """
    Creates and manages the tab bar.

    Attributes:
        root (ctk.CTk): The main window
        ui_elements (UIElements): UI styling settings
        items (list): List of tab items
    """

    def __init__(self, root: ctk.CTk, ui_elements: UIElements):
        self.root = root
        self.ui_elements = ui_elements
        self.items = []

    def create_tab_bar(self, parent: ctk.CTkFrame) -> None:
        """Create tab bar with GitHub styling"""
        tab_frame = ctk.CTkFrame(
            parent,
            fg_color=self.ui_elements.background_color,
            height=50,
            corner_radius=0
        )
        tab_frame.pack(fill="x", pady=(0, 1))

    def add_tab(self, title: str) -> None:
        """Add a new tab"""
        self.items.append({"title": title, "active": False})

    def remove_tab(self, title: str) -> None:
        """Remove a tab"""
        self.items = [item for item in self.items if item["title"] != title]


class MainContentFrame:
    """
    Creates the main content area frame.

    Attributes:
        root (ctk.CTk): The main window
        ui_elements (UIElements): UI styling settings
    """

    def __init__(self, root: ctk.CTk, ui_elements: UIElements):
        self.root = root
        self.ui_elements = ui_elements

    def create_main_frame(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create main content frame with GitHub styling"""
        content_frame = ctk.CTkFrame(
            parent,
            fg_color=self.ui_elements.background_color,
            corner_radius=0
        )
        content_frame.pack(fill="both", expand=True, padx=0, pady=0)
        return content_frame


class ContentAreaManager:
    """
    Manages the main content area of the application.

    This class coordinates the tab bar, main content frame, import section,
    and activity log components.

    Attributes:
        root (ctk.CTk): The main window
        ui_elements (UIElements): UI styling settings
        import_section (ImportSectionManager): Import section manager
        activity_log (ActivityLogManager): Activity log manager
        tab_bar (TabBarManager): Tab bar manager
        main_content_frame (MainContentFrame): Main content frame manager
    """

    def __init__(self,
                 root: ctk.CTk,
                 ui_elements: UIElements,
                 import_section: ImportSectionManager,
                 activity_log: ActivityLogManager):
        """
        Initialize the content area manager.

        Args:
            root: Main window instance
            ui_elements: UI styling instance
            import_section: Import section manager instance
            activity_log: Activity log manager instance
        """
        self.root = root
        self.ui_elements = ui_elements
        self.import_section = import_section
        self.activity_log = activity_log
        self.tab_bar = TabBarManager(self.root, self.ui_elements)
        self.main_content_frame = MainContentFrame(self.root, self.ui_elements)
        self.create_main_content()

    def create_main_content(self) -> None:
        """Create the main content area with tabs and content"""
        # Create tab bar
        self.tab_bar.create_tab_bar(self.root)

        # Create main content frame
        content_frame = self.main_content_frame.create_main_frame(self.root)

        # Add import section
        self.import_section.create_import_section(content_frame)

        # Add activity log
        self.activity_log.create_activity_log(content_frame)

    def update_content(self) -> None:
        """Update content area based on current state"""
        pass

    def get_active_tab(self) -> Optional[str]:
        """
        Get the currently active tab.

        Returns:
            Optional[str]: Title of active tab or None
        """
        for item in self.tab_bar.items:
            if item.get("active"):
                return item["title"]
        return None

    def set_active_tab(self, title: str) -> None:
        """
        Set the active tab.

        Args:
            title: Title of tab to activate
        """
        for item in self.tab_bar.items:
            item["active"] = (item["title"] == title)
        self.update_content()

    def refresh_content(self) -> None:
        """Refresh the content area"""
        self.update_content()