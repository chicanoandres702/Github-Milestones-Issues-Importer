# github_importer/gui/activity_log_model.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class ActivityLogItem:
    """Data class for activity log items"""
    timestamp: str
    icon: str
    msg: str
    level: str = 'info'

class ActivityLogModel:
    """
    Creates custom Activity log items.

    This class is responsible for creating activity log entries
    with proper formatting and structure.
    """

    @staticmethod
    def createActivityLogItem(timestamp: str, icon: str, msg: str, level: str = 'info') -> ActivityLogItem:
        """
        Create a new activity log item.

        Args:
            timestamp: Time of the log entry
            icon: Icon to display
            msg: Log message
            level: Log level (default: 'info')

        Returns:
            ActivityLogItem: Created log item
        """
        return ActivityLogItem(
            timestamp=timestamp,
            icon=icon,
            msg=msg,
            level=level
        )