# github_importer/gui/navigation_manager.py

import customtkinter as ctk
from typing import Callable, Optional, List
from dataclasses import dataclass
from github_importer.gui.ui_elements import UIElements


@dataclass
class NavItem:
    """Data class for navigation items"""
    title: str
    action: Optional[Callable] = None
    type: str = 'button'


class NavButton(ctk.CTkButton):
    """Custom navigation button with GitHub styling"""

    def __init__(self, master: ctk.CTk, title: str, ui_elements: UIElements, **kwargs):
        super().__init__(
            master=master,
            text=title,
            fg_color="transparent",
            hover_color=ui_elements.surface_color,
            text_color=ui_elements.text_color,
            height=32,
            corner_radius=4,
            **kwargs
        )


class ActionButtonsManager:
    """Creates and manages action buttons (Watch, Fork, Star)"""

    def __init__(self, root: ctk.CTk, ui_elements: UIElements):
        self.root = root
        self.ui_elements = ui_elements

    def create_buttons(self, parent: ctk.CTkFrame) -> None:
        """Creates GitHub-style action buttons with counters"""
        for action in [("󰯈 Watch", "12"), ("󰘖 Fork", "5"), ("󰓎 Star", "23")]:
            btn_frame = ctk.CTkFrame(
                parent,
                fg_color=self.ui_elements.secondary_color,
                corner_radius=6,
                height=32
            )
            btn_frame.pack(side="left", padx=4)
            btn_frame.pack_propagate(False)

            btn = ctk.CTkButton(
                btn_frame,
                text=action[0],
                fg_color="transparent",
                hover_color=self.ui_elements.secondary_hover_color,
                text_color=self.ui_elements.text_color,
                height=32,
                corner_radius=6,
                font=("Segoe UI", 12)
            )
            btn.pack(side="left", padx=8)

            # Counter badge
            counter = ctk.CTkLabel(
                btn_frame,
                text=action[1],
                fg_color=self.ui_elements.counter_bg_color,
                text_color=self.ui_elements.text_color,
                corner_radius=10,
                font=("Segoe UI", 11),
                width=30,
                height=20
            )
            counter.pack(side="right", padx=8)


class NavigationManager:
    """
    Manages the navigation bar of the application.

    Attributes:
        root (ctk.CTk): The main window
        ui_elements (UIElements): UI styling settings
        update_repo_callback (Callable): Callback for repository selection changes
        action_buttons (ActionButtonsManager): Manages action buttons
    """

    def __init__(self, root: ctk.CTk, ui_elements: UIElements, update_repo_callback: Callable):
        self.root = root
        self.ui_elements = ui_elements
        self.update_repo_callback = update_repo_callback
        self.action_buttons = ActionButtonsManager(root, ui_elements)
        self.items: List[NavItem] = []

    def create_navigation(self) -> None:
        """Creates the repository-specific navigation bar"""
        nav_bar = ctk.CTkFrame(
            self.root,
            fg_color=self.ui_elements.navbar_color,
            height=50,
            corner_radius=0
        )
        nav_bar.pack(fill="x", pady=(1, 0))
        nav_bar.pack_propagate(False)

        # Repository frame
        repo_frame = ctk.CTkFrame(nav_bar, fg_color="transparent")
        repo_frame.pack(side="left", padx=16, fill="y")

        # Action Buttons
        self.action_buttons.create_buttons(repo_frame)

    def add_nav_item(self, item: NavItem) -> None:
        """
        Add a navigation item.

        Args:
            item: Navigation item to add
        """
        if not isinstance(item, NavItem):
            raise ValueError(f"Invalid item type: {type(item)}")
        self.items.append(item)

    def remove_nav_item(self, item: NavItem) -> None:
        """
        Remove a navigation item.

        Args:
            item: Navigation item to remove
        """
        if item in self.items:
            self.items.remove(item)

    def _create_nav_button(self, title: str, parent: ctk.CTkFrame) -> NavButton:
        """
        Create a navigation button with GitHub styling.

        Args:
            title: Button title
            parent: Parent frame

        Returns:
            NavButton: Created navigation button
        """
        return NavButton(
            master=parent,
            title=title,
            ui_elements=self.ui_elements
        )

    def update_navigation(self) -> None:
        """Update navigation items based on current state"""
        # Implementation for dynamic navigation updates
        pass

    def get_active_nav_item(self) -> Optional[NavItem]:
        """
        Get the currently active navigation item.

        Returns:
            Optional[NavItem]: Currently active navigation item or None
        """
        # Implementation for getting active navigation item
        return next((item for item in self.items if getattr(item, 'active', False)), None)
