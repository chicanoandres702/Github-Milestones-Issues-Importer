# github_importer/gui/header_manager.py

import customtkinter as ctk
from typing import Callable, Optional
from github_importer.gui.ui_elements import UIElements


class HeaderLogoItem:
    """Creates the logo in the header."""

    def __init__(self):
        self.root = None
        self.ui_elements = None

    def create_logo(self, parent: ctk.CTkFrame) -> None:
        logo_label = ctk.CTkLabel(
            parent,
            text="Github Planner",
            text_color=self.ui_elements.text_color,
            font=("Segoe UI", 24)
        )
        logo_label.pack(side="left", padx=(0, 16))


class HeaderSearchItem:
    """Creates the search bar in the header."""

    def __init__(self):
        self.root = None
        self.ui_elements = None

    def create_search(self, parent: ctk.CTkFrame) -> None:
        search_frame = ctk.CTkFrame(
            parent,
            fg_color=self.ui_elements.background_color,
            height=28,
            corner_radius=6
        )
        search_frame.pack(side="left", padx=8)

        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search or jump to...",
            text_color=self.ui_elements.text_color,
            fg_color="transparent",
            border_width=0,
            height=28,
            width=240
        )
        search_entry.pack(side="left", padx=8)


class RepoSelector:
    """Creates a dropdown menu for selecting a repository."""

    def __init__(self, root: ctk.CTk, ui_elements: UIElements, update_repo_callback: Callable):
        self.root = root
        self.ui_elements = ui_elements
        self.repo_selection = ctk.StringVar()
        self.repo_dropdown = None
        self.update_repo_callback = update_repo_callback

    def create_selector(self, parent: ctk.CTkFrame) -> None:
        self.repo_dropdown = ctk.CTkOptionMenu(
            parent,
            variable=self.repo_selection,
            button_color=self.ui_elements.secondary_color,
            button_hover_color=self.ui_elements.secondary_hover_color,
            text_color=self.ui_elements.text_color,
            dropdown_fg_color=self.ui_elements.surface_color,
            dropdown_hover_color=self.ui_elements.dropdown_hover_color,
            dropdown_text_color=self.ui_elements.text_color,
            width=300,
            height=32,
            corner_radius=6,
            font=("Segoe UI", 12),
            dynamic_resizing=False,
            command=self.update_repo_callback
        )
        self.repo_dropdown.pack(side="left", padx=(0, 8))


class HeaderNavigationItemsManager:
    """Creates the navigation items in the header."""

    def __init__(self, ui_elements: UIElements, root: ctk.CTk):
        self.root = root
        self.ui_elements = ui_elements
        self.items = []

    def create_nav_items(self, parent: ctk.CTkFrame) -> None:
        nav_items = ['Pull requests', 'Issues', 'Marketplace', 'Explore']
        for item in nav_items:
            nav_button = ctk.CTkButton(
                parent,
                text=item,
                fg_color="transparent",
                hover_color=self.ui_elements.surface_color,
                text_color=self.ui_elements.text_color,
                height=32,
                corner_radius=4
            )
            nav_button.pack(side="left", padx=4)


class HeaderManager:
    """
    Manages the header section of the application.

    Attributes:
        root (ctk.CTk): The main window
        ui_elements (UIElements): UI styling settings
        update_repo_callback (Callable): Callback for repository selection changes
    """

    def __init__(self, root: ctk.CTk, ui_elements: UIElements, update_repo_callback: Callable):
        self.root = root
        self.ui_elements = ui_elements
        self.header_logo = HeaderLogoItem()
        self.header_search = HeaderSearchItem()
        self.header_nav_items = HeaderNavigationItemsManager(self.ui_elements, self.root)
        self.repo_selector = RepoSelector(self.root, self.ui_elements, update_repo_callback)
        self.create_header()

    def create_header(self) -> None:
        """Creates GitHub's top header with navigation and user controls"""
        # Main header bar
        header = ctk.CTkFrame(
            self.root,
            fg_color=self.ui_elements.header_color,
            height=60,
            corner_radius=0
        )
        header.pack(fill="x", pady=0)
        header.pack_propagate(False)

        # Left section - Logo and search
        left_section = ctk.CTkFrame(header, fg_color="transparent")
        left_section.pack(side="left", padx=16, fill="y")

        # Header Logo
        self.header_logo.root = self.root
        self.header_logo.ui_elements = self.ui_elements
        self.header_logo.create_logo(left_section)

        # Repo Selector
        self.repo_selector.create_selector(left_section)

        # Header Search
        self.header_search.root = self.root
        self.header_search.ui_elements = self.ui_elements
        self.header_search.create_search(left_section)

        # Right section - Navigation items
        right_section = ctk.CTkFrame(header, fg_color="transparent")
        right_section.pack(side="right", padx=16, fill="y")

        # Header Nav Items
        self.header_nav_items.root = self.root
        self.header_nav_items.ui_elements = self.ui_elements
        self.header_nav_items.create_nav_items(right_section)