# github_importer/gui/textbox_logger.py

import logging
import customtkinter as ctk
from typing import Optional
from datetime import datetime
from github_importer.gui.ui_elements import UIElements


class TextboxLogger(logging.Handler):
    """
    Custom logging handler that displays log messages in a customtkinter textbox.

    This handler formats log messages with GitHub-style icons and colors,
    displaying them in a specified textbox widget.

    Attributes:
        textbox (Optional[ctk.CTkTextbox]): The textbox where logs will be displayed
        ui_elements (UIElements): UI styling settings
    """

    def __init__(self, ui_elements: UIElements):
        """
        Initialize the textbox logger.

        Args:
            ui_elements: UI styling instance
        """
        super().__init__()
        self.textbox: Optional[ctk.CTkTextbox] = None
        self.ui_elements = ui_elements

        # Set up a formatter
        formatter = logging.Formatter('%(message)s')
        self.setFormatter(formatter)

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record by inserting the formatted message into the textbox.

        Args:
            record: The log record to emit
        """
        if not self.textbox:
            return

        try:
            # Format timestamp
            timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

            # GitHub-style status icons
            level_icons = {
                'INFO': '󰆼',  # Check circle
                'ERROR': '󰅚',  # X circle
                'WARNING': '󰀦',  # Warning triangle
                'DEBUG': '󰌄'  # Debug icon
            }

            # GitHub-style colors
            level_colors = {
                'INFO': self.ui_elements.success_color,
                'ERROR': self.ui_elements.error_color,
                'WARNING': '#D29922',  # GitHub warning color
                'DEBUG': self.ui_elements.text_secondary_color
            }

            # Get icon and color for log level
            icon = level_icons.get(record.levelname, '')
            color = level_colors.get(record.levelname, self.ui_elements.text_color)

            # Format and insert the log message
            self._insert_log_entry(timestamp, icon, record.getMessage(), color)

            # Scroll to the end
            self.textbox.see('end')

        except Exception as e:
            # Fallback to stderr in case of error
            self.handleError(record)

    def _insert_log_entry(self, timestamp: str, icon: str, message: str, color: str) -> None:
        """
        Insert a formatted log entry into the textbox.

        Args:
            timestamp: Time of the log entry
            icon: Icon to display
            message: Log message
            color: Color for the icon
        """
        # Insert components with their respective tags
        self.textbox.insert('end', f"{timestamp} ", ('timestamp',))
        self.textbox.insert('end', f"{icon} ", ('icon',))
        self.textbox.insert('end', f"{message}\n", ('message',))

        # Configure tags with GitHub styling
        self.textbox.tag_config('timestamp',
                                foreground=self.ui_elements.text_secondary_color)
        self.textbox.tag_config('icon', foreground=color)
        self.textbox.tag_config('message',
                                foreground=self.ui_elements.text_color)

    def set_textbox(self, textbox: ctk.CTkTextbox) -> None:
        """
        Set the textbox widget for displaying logs.

        Args:
            textbox: The textbox widget to use
        """
        self.textbox = textbox

    def clear(self) -> None:
        """Clear all log entries from the textbox."""
        if self.textbox:
            self.textbox.delete('1.0', 'end')

    def get_log_contents(self) -> str:
        """
        Get all log contents as text.

        Returns:
            str: Complete log contents
        """
        if self.textbox:
            return self.textbox.get('1.0', 'end-1c')
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

    def handle_error(self, record: logging.LogRecord) -> None:
        """
        Handle any errors that occur during logging.

        Args:
            record: The log record that caused the error
        """
        if self.textbox:
            self.textbox.insert('end',
                                "Error occurred while logging\n",
                                ('error',))
            self.textbox.tag_config('error',
                                    foreground=self.ui_elements.error_color)

    def format_level(self, level: str) -> str:
        """
        Format the log level text with GitHub styling.

        Args:
            level: Log level to format

        Returns:
            str: Formatted log level text
        """
        return f"[{level}]"