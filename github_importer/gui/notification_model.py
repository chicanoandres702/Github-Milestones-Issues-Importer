# github_importer/gui/notification_model.py

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class NotificationItem:
    """
    Data class for notification items.

    Attributes:
        title (str): The notification title
        message (str): The main notification message
        level (str): The notification level (info, error, success, warning)
        timestamp (datetime): When the notification was created
        duration (int): How long to show the notification (in milliseconds)
    """
    title: str
    message: str
    level: str = 'info'
    timestamp: Optional[datetime] = None
    duration: int = 3000  # Default duration: 3 seconds

    def __post_init__(self):
        """Set timestamp if not provided"""
        if self.timestamp is None:
            self.timestamp = datetime.now()

    @property
    def formatted_timestamp(self) -> str:
        """Get formatted timestamp string"""
        return self.timestamp.strftime("%H:%M:%S")

    @property
    def icon(self) -> str:
        """Get the appropriate icon for the notification level"""
        icons = {
            'success': '󰄬',  # Checkmark
            'error': '󰅚',  # X mark
            'warning': '󰀦',  # Warning triangle
            'info': '󰋼'  # Info icon
        }
        return icons.get(self.level, '󰋼')

    @property
    def color(self) -> str:
        """Get the appropriate color for the notification level"""
        colors = {
            'success': '#2EA043',  # GitHub success green
            'error': '#F85149',  # GitHub error red
            'warning': '#D29922',  # GitHub warning yellow
            'info': '#58A6FF'  # GitHub info blue
        }
        return colors.get(self.level, '#58A6FF')


class NotificationModel:
    """
    Creates and manages notification items.

    This class is responsible for creating notification items with proper
    formatting and structure, following GitHub's notification patterns.
    """

    @staticmethod
    def createNotificationItem(
            title: str,
            message: str,
            level: str = 'info',
            duration: int = 3000
    ) -> NotificationItem:
        """
        Create a new notification item.

        Args:
            title: The notification title
            message: The main notification message
            level: Notification level (info, error, success, warning)
            duration: How long to show the notification (in milliseconds)

        Returns:
            NotificationItem: Created notification item

        Examples:
            >>> model = NotificationModel()
            >>> item = model.createNotificationItem(
            ...     "Success",
            ...     "Operation completed",
            ...     "success"
            ... )
        """
        return NotificationItem(
            title=title,
            message=message,
            level=level,
            duration=duration
        )

    @staticmethod
    def create_success_notification(
            message: str,
            title: str = "Success"
    ) -> NotificationItem:
        """Create a success notification"""
        return NotificationItem(
            title=title,
            message=message,
            level='success'
        )

    @staticmethod
    def create_error_notification(
            message: str,
            title: str = "Error"
    ) -> NotificationItem:
        """Create an error notification"""
        return NotificationItem(
            title=title,
            message=message,
            level='error'
        )

    @staticmethod
    def create_warning_notification(
            message: str,
            title: str = "Warning"
    ) -> NotificationItem:
        """Create a warning notification"""
        return NotificationItem(
            title=title,
            message=message,
            level='warning'
        )

    @staticmethod
    def create_info_notification(
            message: str,
            title: str = "Info"
    ) -> NotificationItem:
        """Create an info notification"""
        return NotificationItem(
            title=title,
            message=message,
            level='info'
        )

    def validate_notification(self, item: NotificationItem) -> bool:
        """
        Validate a notification item.

        Args:
            item: The notification item to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(item, NotificationItem):
            return False

        if not item.title or not item.message:
            return False

        if item.level not in ['info', 'success', 'warning', 'error']:
            return False

        if item.duration <= 0:
            return False

        return True

    def format_notification(self, item: NotificationItem) -> dict:
        """
        Format a notification item for display.

        Args:
            item: The notification item to format

        Returns:
            dict: Formatted notification data
        """
        return {
            'title': item.title,
            'message': item.message,
            'level': item.level,
            'icon': item.icon,
            'color': item.color,
            'timestamp': item.formatted_timestamp,
            'duration': item.duration
        }