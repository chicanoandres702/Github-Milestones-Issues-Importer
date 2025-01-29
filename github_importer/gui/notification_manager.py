# github_importer/gui/notification_manager.py

import customtkinter as ctk
from typing import List, Optional
from github_importer.gui.ui_elements import UIElements
from github_importer.gui.notification_model import NotificationItem


class NotificationManager:
    """
    Shows temporary pop-up messages in GitHub style.

    This class manages the creation and display of temporary notifications,
    following GitHub's notification design patterns.

    Attributes:
        root (ctk.CTk): The main window to attach notifications to
        ui_elements (UIElements): UI styling settings
        items (List[NotificationItem]): List of active notifications
    """

    def __init__(self, root: ctk.CTk, ui_elements: UIElements):
        """
        Initialize the notification manager.

        Args:
            root: Main window instance
            ui_elements: UI styling instance
        """
        self.root = root
        self.ui_elements = ui_elements
        self.items: List[NotificationItem] = []
        self._active_notifications: List[ctk.CTkToplevel] = []
        self._notification_spacing = 10

    def addItem(self, item: NotificationItem) -> None:
        """
        Add and display a new notification.

        Args:
            item: The notification item to display
        """
        if not isinstance(item, NotificationItem):
            raise ValueError(f"Invalid item type: {type(item)}")

        self.items.append(item)
        self._show_notification(item)
        self._update_notification_positions()

    def destroy_item(self, item: NotificationItem) -> None:
        """
        Remove a notification item.

        Args:
            item: The notification item to remove
        """
        if item in self.items:
            self.items.remove(item)

    def _show_notification(self, item: NotificationItem) -> None:
        """
        Display a GitHub-style notification.

        Args:
            item: The notification item to display
        """
        try:
            # Create notification window
            notification = ctk.CTkToplevel(self.root)
            notification.title("")
            notification.geometry("300x100")
            notification.resizable(False, False)
            notification.overrideredirect(True)
            notification.attributes('-topmost', True)

            # Position in top-right corner
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            base_y = screen_height - 120
            offset = len(self._active_notifications) * (110 + self._notification_spacing)
            notification.geometry(f"+{screen_width - 320}+{base_y - offset}")

            # Get color based on notification level
            bg_color = {
                "success": self.ui_elements.success_color,
                "error": self.ui_elements.error_color,
                "warning": "#D29922",  # GitHub warning color
                "info": self.ui_elements.secondary_color
            }.get(item.level, self.ui_elements.secondary_color)

            # Main frame
            main_frame = ctk.CTkFrame(
                notification,
                fg_color=self.ui_elements.surface_color,
                corner_radius=6,
                border_width=1,
                border_color=self.ui_elements.border_color
            )
            main_frame.pack(fill="both", expand=True, padx=2, pady=2)

            # Content frame
            content_frame = ctk.CTkFrame(
                main_frame,
                fg_color="transparent"
            )
            content_frame.pack(fill="both", expand=True, padx=12, pady=12)

            # Icon
            icon = {
                "success": "󰄬",  # Checkmark
                "error": "󰅚",  # X mark
                "warning": "󰀦",  # Warning triangle
                "info": "󰋼"  # Info icon
            }.get(item.level, "󰋼")

            icon_label = ctk.CTkLabel(
                content_frame,
                text=icon,
                text_color=bg_color,
                font=("Segoe UI", 16)
            )
            icon_label.pack(side="left", padx=(0, 8))

            # Text frame
            text_frame = ctk.CTkFrame(
                content_frame,
                fg_color="transparent"
            )
            text_frame.pack(side="left", fill="both", expand=True)

            # Title
            title_label = ctk.CTkLabel(
                text_frame,
                text=item.title,
                text_color=self.ui_elements.text_color,
                font=("Segoe UI", 12, "bold"),
                anchor="w"
            )
            title_label.pack(fill="x")

            # Message
            message_label = ctk.CTkLabel(
                text_frame,
                text=item.message,
                text_color=self.ui_elements.text_secondary_color,
                font=("Segoe UI", 11),
                anchor="w",
                justify="left",
                wraplength=200
            )
            message_label.pack(fill="x")

            # Close button frame
            close_frame = ctk.CTkFrame(
                content_frame,
                fg_color="transparent",
                width=20,
                height=20
            )
            close_frame.pack(side="right", padx=(8, 0))

            # Close button
            close_button = ctk.CTkButton(
                close_frame,
                text="×",
                width=20,
                height=20,
                fg_color="transparent",
                hover_color=self.ui_elements.secondary_hover_color,
                text_color=self.ui_elements.text_secondary_color,
                font=("Segoe UI", 14),
                command=lambda: self._close_notification(notification, item)
            )
            close_button.place(relx=0.5, rely=0, anchor="n")

            # Store notification window
            self._active_notifications.append(notification)

            # Auto-close notification
            notification.after(item.duration, lambda: self._close_notification(notification, item))

        except Exception as e:
            print(f"Error showing notification: {e}")

    def _close_notification(self, notification: ctk.CTkToplevel, item: NotificationItem) -> None:
        """
        Close a notification and remove it from items list.

        Args:
            notification: The notification window to close
            item: The notification item to remove
        """
        try:
            if notification in self._active_notifications:
                self._active_notifications.remove(notification)
            notification.destroy()
            self.destroy_item(item)
            self._update_notification_positions()
        except Exception as e:
            print(f"Error closing notification: {e}")

    def _update_notification_positions(self) -> None:
        """Update the positions of all active notifications."""
        try:
            screen_height = self.root.winfo_screenheight()
            base_y = screen_height - 120

            for i, notification in enumerate(self._active_notifications):
                offset = i * (110 + self._notification_spacing)
                y_pos = base_y - offset

                current_geometry = notification.geometry()
                current_x = int(current_geometry.split("+")[1])

                notification.geometry(f"+{current_x}+{y_pos}")
        except Exception as e:
            print(f"Error updating notification positions: {e}")

    def clear_all(self) -> None:
        """Clear all active notifications."""
        for notification in self._active_notifications[:]:
            notification.destroy()
        self._active_notifications.clear()
        self.items.clear()

    def get_active_notifications(self) -> List[NotificationItem]:
        """
        Get list of active notifications.

        Returns:
            List[NotificationItem]: List of currently active notifications
        """
        return self.items.copy()