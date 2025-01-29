# github_importer/gui/status_interface.py

from typing import Optional
from datetime import datetime
from github_importer.gui.activity_log_model import ActivityLogModel, ActivityLogItem
from github_importer.gui.notification_model import NotificationModel, NotificationItem
from github_importer.gui.notification_manager import NotificationManager

class StatusInterface:
    """
    A status interface to handle status updates with GitHub-style notifications.

    This class abstracts the process of handling status updates, allowing
    the application to maintain compatibility with code that expects a status
    label, while displaying status updates as GitHub-style notifications.

    Attributes:
        main_window (MainWindow): Reference to the main application window
        notification_manager (NotificationManager): The notification manager instance
        activity_log_model (ActivityLogModel): Model for creating activity log items
        notification_model (NotificationModel): Model for creating notifications
    """

    def __init__(self, main_window: 'MainWindow', notification_manager: NotificationManager):
        """
        Initialize the status interface.

        Args:
            main_window: Reference to the main application window
            notification_manager: The notification manager instance
        """
        self.main_window = main_window
        self.notification_manager = notification_manager
        self.activity_log_model = ActivityLogModel()
        self.notification_model = NotificationModel()

    def update(self, message: str, level: str = 'info') -> None:
        """
        Update status with GitHub-style notifications.

        This method handles status updates by:
        1. Logging the message
        2. Showing it in the activity log
        3. Displaying a notification

        Args:
            message: The status message to display
            level: Message level (info, error, success)
        """
        if self.main_window and self.notification_manager:
            # Get current timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Get appropriate icon based on level
            icon = self._get_level_icon(level)

            # Log the message
            self._log_message(message, level)

            # Show in activity log
            self._update_activity_log(timestamp, icon, message, level)

            # Show notification
            self._show_notification(message, level)
        else:
            # Fallback logging when dependencies aren't available
            print(f"{level.upper()}: {message}")

    def _get_level_icon(self, level: str) -> str:
        """
        Get the appropriate icon for the message level.

        Args:
            level: Message level

        Returns:
            str: Icon character for the level
        """
        icons = {
            'success': '󰄬',  # Checkmark
            'error': '󰅚',    # X mark
            'warning': '󰀦',  # Warning triangle
            'info': '󰋼'      # Info icon
        }
        return icons.get(level, '󰋼')

    def _log_message(self, message: str, level: str) -> None:
        """
        Log the message using the appropriate log level.

        Args:
            message: Message to log
            level: Log level
        """
        if hasattr(self.main_window, 'logger'):
            if level == 'error':
                self.main_window.logger.error(message)
            elif level == 'warning':
                self.main_window.logger.warning(message)
            else:
                self.main_window.logger.info(message)

    def _update_activity_log(self, timestamp: str, icon: str, message: str, level: str) -> None:
        """
        Update the activity log with the message.

        Args:
            timestamp: Current timestamp
            icon: Level-appropriate icon
            message: Message to display
            level: Message level
        """
        if hasattr(self.main_window, 'activity_log'):
            log_item = self.activity_log_model.createActivityLogItem(
                timestamp=timestamp,
                icon=icon,
                msg=message,
                level=level
            )
            self.main_window.activity_log.addItem(log_item)

    def _show_notification(self, message: str, level: str) -> None:
        """
        Show a notification with the message.

        Args:
            message: Message to display
            level: Message level
        """
        notification_item = self.notification_model.createNotificationItem(
            title=level.capitalize(),
            message=message,
            level=level
        )
        self.notification_manager.addItem(notification_item)

    def clear_status(self) -> None:
        """Clear any existing status messages."""
        if hasattr(self.main_window, 'activity_log'):
            self.main_window.activity_log.clear_log()

    def get_current_status(self) -> Optional[str]:
        """
        Get the most recent status message.

        Returns:
            Optional[str]: Most recent status message or None if no messages
        """
        if hasattr(self.main_window, 'activity_log'):
            log_contents = self.main_window.activity_log.get_log_contents()
            if log_contents:
                return log_contents.splitlines()[-1]
        return None

    def update_progress(self, message: str, progress: float) -> None:
        """
        Update status with progress information.

        Args:
            message: Status message
            progress: Progress value (0-1)
        """
        progress_message = f"{message} ({progress:.0%})"
        self.update(progress_message, 'info')

    def handle_error(self, error: Exception, context: str = '') -> None:
        """
        Handle an error with appropriate status updates.

        Args:
            error: The exception that occurred
            context: Additional context for the error
        """
        error_message = f"{context + ': ' if context else ''}{str(error)}"
        self.update(error_message, 'error')

    def handle_success(self, message: str) -> None:
        """
        Handle a success status update.

        Args:
            message: Success message to display
        """
        self.update(message, 'success')

    def handle_warning(self, message: str) -> None:
        """
        Handle a warning status update.

        Args:
            message: Warning message to display
        """
        self.update(message, 'warning')