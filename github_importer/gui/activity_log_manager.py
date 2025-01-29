# github_importer/gui/activity_log_manager.py

import customtkinter as ctk
from typing import List, Optional
from datetime import datetime
from github_importer.gui.ui_elements import UIElements
from github_importer.gui.textbox_logger import TextboxLogger
from github_importer.gui.activity_log_model import ActivityLogItem


class ActivityLogHeaderItem:
    """Creates the activity log header."""

    def __init__(self):
        self.root = None
        self.ui_elements = None

    def create_header(self, parent: ctk.CTkFrame) -> None:
        header_frame = ctk.CTkFrame(
            parent,
            fg_color=self.ui_elements.secondary_color,
            height=40,
            corner_radius=6
        )
        header_frame.pack(fill="x")

        header_label = ctk.CTkLabel(
            header_frame,
            text="󰑍 Activity",
            text_color=self.ui_elements.text_color,
            font=("Segoe UI", 14, "bold")
        )
        header_label.pack(side="left", padx=16, pady=8)


class ActivityLogTextItem(ctk.CTkTextbox):
    """Custom textbox for activity log with GitHub styling."""

    def __init__(self, master: ctk.CTkFrame, ui_elements: UIElements, **kwargs):
        super().__init__(
            master=master,
            wrap="word",
            fg_color=ui_elements.background_color,
            text_color=ui_elements.text_color,
            font=("Segoe UI", 11),
            border_color=ui_elements.border_color,
            border_width=1,
            **kwargs
        )
        self.ui_elements = ui_elements

    def _format_log(self, timestamp: str, icon: str, msg: str, level: str = 'info') -> None:
        """Format and insert a log entry with GitHub styling"""
        # Get color based on level
        level_colors = {
            'info': self.ui_elements.text_color,
            'error': self.ui_elements.error_color,
            'warning': '#D29922',  # GitHub warning color
            'success': self.ui_elements.success_color
        }
        color = level_colors.get(level, self.ui_elements.text_color)

        self.insert('end', f"{timestamp} ", ('timestamp',))
        self.insert('end', f"{icon} ", ('icon',))
        self.insert('end', f"{msg}\n", ('message',))

        self.tag_config('timestamp', foreground=self.ui_elements.text_secondary_color)
        self.tag_config('icon', foreground=color)
        self.tag_config('message', foreground=self.ui_elements.text_color)


class ActivityLogManager:
    """
    Manages the activity log section of the application.

    Attributes:
        ui_elements (UIElements): UI styling settings
        textbox_logger (TextboxLogger): Logger for text display
        header (ActivityLogHeaderItem): Activity log header manager
        items (List[ActivityLogTextItem]): List of log items
        root (ctk.CTk): The main window
    """

    def __init__(self, ui_elements: UIElements, textbox_logger: TextboxLogger, root: ctk.CTk):
        self.ui_elements = ui_elements
        self.textbox_logger = textbox_logger
        self.header = ActivityLogHeaderItem()
        self.root = root
        self.items: List[ActivityLogTextItem] = []

    def create_activity_log(self, parent: ctk.CTkFrame) -> None:
        """Create the complete activity log section with GitHub styling"""
        log_frame = ctk.CTkFrame(
            parent,
            fg_color=self.ui_elements.surface_color,
            corner_radius=6
        )
        log_frame.pack(fill="both", expand=True)

        # Activity Log Header
        self.header.root = self.root
        self.header.ui_elements = self.ui_elements
        self.header.create_header(log_frame)

        # Activity log text area
        activity_log_text_item = ActivityLogTextItem(log_frame, self.ui_elements)
        activity_log_text_item.pack(fill="both", expand=True, padx=16, pady=16)
        self.textbox_logger.textbox = activity_log_text_item
        self.items.append(activity_log_text_item)

    def addItem(self, item: ActivityLogItem) -> None:
        """
        Add and display a new log item.

        Args:
            item: Activity log item to add
        """
        if not isinstance(item, ActivityLogItem):
            raise ValueError(f"Invalid item type: {type(item)}")

        if self.items:
            # Get appropriate icon based on level
            icons = {
                'info': '󰋼',  # Info icon
                'error': '󰅚',  # X mark
                'warning': '󰀦',  # Warning triangle
                'success': '󰄬'  # Checkmark
            }
            icon = icons.get(item.level, '󰋼')

            # If timestamp is empty, use current time
            timestamp = item.timestamp if item.timestamp else datetime.now().strftime("%H:%M:%S")

            self.items[0]._format_log(
                timestamp=timestamp,
                icon=icon,
                msg=item.msg,
                level=item.level
            )

    def destroy_item(self, item: ActivityLogItem) -> None:
        """
        Remove a log item.

        Args:
            item: Activity log item to remove
        """
        # In this implementation, we don't actually remove items from the text widget
        pass

    def clear_log(self) -> None:
        """Clear all log entries"""
        if self.items:
            self.items[0].delete('1.0', 'end')

    def get_log_contents(self) -> str:
        """
        Get all log contents as text.

        Returns:
            str: Complete log contents
        """
        if self.items:
            return self.items[0].get('1.0', 'end-1c')
        return ""

    def export_log(self, filename: str) -> None:
        """
        Export log contents to a file.

        Args:
            filename: Name of file to export to
        """
        contents = self.get_log_contents()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(contents)