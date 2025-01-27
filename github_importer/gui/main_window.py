import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from github_importer.utils.logger import Logger
from github_importer.import_export.data_importer import DataImporter
from github_importer.github_api.github_client import GitHubClient
from github_importer.utils.token_storage import TokenStorage
from github_importer.auth.auth_manager import AuthManager
from github_importer.config.config import Config
import logging
from dataclasses import dataclass
from typing import List, TypeVar, Generic, Callable
from abc import ABC, abstractmethod

class UIElements:
    """
    **Description:**
    Stores common UI styles.

    Holds colors and other styling settings used throughout the app,
    ensuring a consistent look.

    **Attributes:**
        - `background_color` (str): Main background color.
        - `surface_color` (str):  The color of surfaces like cards.
        - `header_color` (str): The color of the header.
        - `primary_color` (str): The color for main buttons.
        - `primary_hover_color` (str): The color when you hover on main buttons.
        - `secondary_color` (str): The color for secondary buttons.
        - `secondary_hover_color` (str): The color when you hover on secondary buttons.
        - `border_color` (str): The color of borders.
        - `text_color` (str): The main text color.
        - `text_secondary_color` (str): A secondary text color.
        - `accent_color` (str): The color for links and highlights.
        - `error_color` (str): The color for error states.
        - `success_color` (str): Success states color.
        - `tab_active_color` (str): The color for the active tab.
        - `navbar_color` (str): The color of the navigation bar.
        - `counter_bg_color` (str): The background color for badge/counters.
        - `dropdown_hover_color` (str): The color when you hover on dropdown items.

    **Usage:**
        Create an instance of `UIElements` to access the stored styles.

    **Example:**
        ```python
        ui_elements = UIElements()
        print(ui_elements.background_color) # Output: '#0D1117'
        ```
    """
    def __init__(self):
        # GitHub's exact color palette
        self.background_color = '#0D1117'
        self.surface_color = '#161B22'
        self.header_color = '#010409'
        self.primary_color = '#2EA043'
        self.primary_hover_color = '#3FB950'
        self.secondary_color = '#21262D'
        self.secondary_hover_color = '#30363D'
        self.border_color = '#30363D'
        self.text_color = '#C9D1D9'
        self.text_secondary_color = '#8B949E'
        self.accent_color = '#58A6FF'
        self.error_color = '#F85149'
        self.success_color = '#2EA043'
        self.tab_active_color = '#1F6FEB'
        self.navbar_color = '#161B22'
        self.counter_bg_color = '#30363D'
        self.dropdown_hover_color = '#1F6FEB'

T = TypeVar('T')
@dataclass
class NotificationItem:
    title: str
    message: str
    level: str = 'info'

class Manager(Generic[T], ABC):
  def __init__(self):
    self.items: List[T] = []
  @abstractmethod
  def addItem(self, item: T):
    pass
  @abstractmethod
  def destroy_item(self, item: T):
    pass

class NotificationManager(Manager[NotificationItem]):
    """
    **Description:**
    Shows temporary pop-up messages.

    Creates and displays short-lived notifications for user feedback, like a little alert.

    **Attributes:**
        - `root` (ctk.CTk): The main window to attach alerts to.
        - `ui_elements` (UIElements): The style settings to use.
        - `items` (list): List of NotificationItems

    **Methods:**
        - `addItem(item)`: shows a notification.
        - `destroy_item(item)`: removes and destroys the item

    **Usage:**
        1.  Create a `NotificationManager`.
        2.  Tell it where to show (set `root` and `ui_elements`).
        3.  Call `addItem` to display the message.
        4. Call `destroy_item` to clean up a notification

    **Example:**
         ```python
         notification_manager = NotificationManager()
         notification_manager.root = self.root
         notification_manager.ui_elements = self.ui_elements
         item = NotificationItem('Error', "Could not load repositories", 'error')
          notification_manager.addItem(item)
         ```
    """
    def __init__(self, root, ui_elements):
        self.root = root
        self.ui_elements = ui_elements
        super().__init__()

    def addItem(self, item: NotificationItem):
        if not isinstance(item, NotificationItem):
            raise ValueError(f"Invalid item type: {type(item)}")
        self.items.append(item)
        self._show_notification(item)

    def destroy_item(self, item: NotificationItem):
        if item in self.items:
            self.items.remove(item)

    def _show_notification(self, item: NotificationItem):
        """
        Displays GitHub-style notifications for user feedback.
        Creates a temporary overlay notification that matches GitHub's design.

        Args:
            item(NotificationItem): The notification item.
        """
        # Create notification window with GitHub styling
        notification = ctk.CTkToplevel(self.root)
        notification.title("")
        notification.geometry("300x100")
        notification.resizable(False, False)

        # Remove window decorations for clean look
        notification.overrideredirect(True)

        # Position in top-right corner (GitHub style)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        notification.geometry(f"+{screen_width - 320}+{screen_height - 120}")

        # Notification styling based on level
        bg_color = {
            "success": self.ui_elements.success_color,
            "error": self.ui_elements.error_color,
            "info": self.ui_elements.secondary_color
        }.get(item.level, self.ui_elements.secondary_color)

        # Create notification content
        frame = ctk.CTkFrame(
            notification,
            fg_color=self.ui_elements.surface_color,
            corner_radius=6,
            border_width=1,
            border_color=self.ui_elements.border_color
        )
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Add icon based on notification type
        icon = {
            "success": "󰄬",  # Checkmark
            "error": "󰅚",  # X mark
            "info": "󰋼"  # Info icon
        }.get(item.level, "󰋼")

        icon_label = ctk.CTkLabel(
            frame,
            text=icon,
            text_color=bg_color,
            font=("Segoe UI", 16)
        )
        icon_label.pack(side="left", padx=(12, 8), pady=12)

        # Add title and message
        text_frame = ctk.CTkFrame(frame, fg_color="transparent")
        text_frame.pack(fill="both", expand=True, padx=(0, 12), pady=12)

        title_label = ctk.CTkLabel(
            text_frame,
            text=item.title,
            text_color=self.ui_elements.text_color,
            font=("Segoe UI", 12, "bold")
        )
        title_label.pack(anchor="w")

        message_label = ctk.CTkLabel(
            text_frame,
            text=item.message,
            text_color=self.ui_elements.text_secondary_color,
            font=("Segoe UI", 11)
        )
        message_label.pack(anchor="w")

        # Auto-close notification after 3 seconds
        notification.after(3000, notification.destroy)
        self.destroy_item(item)

class NotificationModel:
  """
    **Description:**
    Creates custom notifications.

    Manages custom notifications.

    **Methods:**
         - `createNotificationItem(title, message, level)`: Creates a new notification item

     **Usage:**
        1. Instantiate the `NotificationModel` class.
        2. Use its `createNotificationItem` to create notification messages.

    **Example:**
        ```python
         creator = NotificationModel()
         item = creator.createNotificationItem("Error", "Failed to load", level='error')
        ```
    """
  def createNotificationItem(self, title, message, level='info'):
      return NotificationItem(title, message, level)

class TextboxLogger(logging.Handler):
    """
    **Description:**
    Displays log messages in a text box.

    Takes log messages and shows them in a specific text box in real time.

    **Attributes:**
        - `textbox` (ctk.CTkTextbox): The text box for showing logs.
        - `ui_elements` (UIElements): The styling to use.

    **Methods:**
        - `emit(record)`: Puts the log message into the text box.

    **Usage:**
         1. Create a `TextboxLogger`.
         2.  Tell it where to show logs (set `textbox` and `ui_elements`).
         3.  Add it to your logger instance to start showing logs.

    **Example:**
        ```python
         textbox_logger = TextboxLogger()
         textbox_logger.textbox = self.activity_log.log_text
         textbox_logger.ui_elements = self.ui_elements
         self.logger.addHandler(textbox_logger)
         ```
    """
    def __init__(self, ui_elements):
        """
        Initializes the handler with a textbox.

        Args:
            textbox (ctk.CTkTextbox): The textbox where log messages will be displayed.
            ui_elements (UIElements): instance of UIElements for styling the textbox.
        """
        super().__init__()
        self.textbox = None
        self.ui_elements = ui_elements

    def emit(self, record):
        """
        Emits a log record by inserting the formatted message into the textbox.

        Args:
            record (logging.LogRecord): The log record to emit.
        """
        msg = self.format(record)

        timestamp = record.created.strftime("%H:%M:%S")

        # GitHub-style status icons
        level_icons = {
            'INFO': '󰆼',  # Check circle
            'ERROR': '󰅚',  # X circle
            'WARNING': '󰀦'  # Warning triangle
        }

        level_colors = {
            'INFO': self.ui_elements.success_color,
            'ERROR': self.ui_elements.error_color,
            'WARNING': '#D29922'  # GitHub warning color
        }

        icon = level_icons.get(record.levelname, '')
        color = level_colors.get(record.levelname, self.ui_elements.text_color)


        # Insert GitHub-style log entry
        self.textbox.insert('end', f"{timestamp} ", ('timestamp',))
        self.textbox.insert('end', f"{icon} ", ('icon',))
        self.textbox.insert('end', f"{msg}\n", ('message',))

        # Apply GitHub-style formatting
        self.textbox.tag_config('timestamp', foreground=self.ui_elements.text_secondary_color)
        self.textbox.tag_config('icon', foreground=color)
        self.textbox.tag_config('message', foreground=self.ui_elements.text_color)

        self.textbox.see('end')

class NavButton(ctk.CTkButton):
    """
    **Description:**
    Creates a single navigation button.

    A reusable button component for navigation bars or headers, customizable by title.

    **Attributes:**
         - `title` (str): The text to show on the button.
         - `ui_elements` (UIElements): The styling to use.

    **Usage:**
         1. Create a `NavButton` with a title and ui_elements.
         2. Use this button in your navigation areas.

    **Example:**
        ```python
        nav_button = NavButton(title="Pull requests", ui_elements=self.ui_elements)
        nav_button.pack(side="left", padx=4)
        ```
    """
    def __init__(self, master, title, ui_elements, **kwargs):
        super().__init__(
             master = master,
             text=title,
             fg_color="transparent",
             hover_color=ui_elements.surface_color,
             text_color=ui_elements.text_color,
             height=32,
             corner_radius=4,
             **kwargs
        )

@dataclass
class NavItem:
   """
    **Description:**
    Creates a single navigation item

    A data holder that has the type, title, url or a command.
    """
   title: str
   action: Callable = None
   type: str = 'button'

class NavButtonItem(NavButton):
    """
       **Description:**
        Creates a single navigation button with style.

    A button component for navigation bars or headers, customizable by title.
    """
    def __init__(self, master, title, ui_elements, **kwargs):
       super().__init__(master=master, title=title, ui_elements=ui_elements, **kwargs)

class NavTextItem:
    """
       **Description:**
        Creates a single navigation text item with style.

        A text component for navigation bars or headers, customizable by title.
    """
    def __init__(self, title, ui_elements, **kwargs):
          self.title = title
          self.ui_elements = ui_elements

class NavItemModel:
  """
    **Description:**
    Creates a single navigation item.

    A data holder that has the type, title, url or a command.

     **Methods:**
         - `create_nav_button_item(title)`: Creates a new button based NavItem
         - `create_nav_text_item(title)`: Creates a new text based NavItem.


    **Usage:**
        1. Instantiate the `NavItemModel` class
        2. Use one of its factory methods to generate a new NavItem.

    **Example:**
         ```python
         creator = NavItemModel(self.ui_elements)
         item = creator.create_nav_button_item(title="Pull requests")
        ```
    """
  def __init__(self, ui_elements):
     self.ui_elements = ui_elements
  def create_nav_button_item(self, title):
    return NavItem(title=title, type='button')
  def create_nav_text_item(self, title):
      return NavItem(title=title, type='text')

class HeaderNavigationItemsManager(Manager[NavItem]):
    """
    **Description:**
    Creates the navigation items in the header.

    Manages links to different areas of the app, like 'Pull requests' and 'Issues.'

         **Attributes:**
             - `root` (ctk.CTk): The main window to attach them to.
             - `ui_elements` (UIElements): The styling to use.
              - `items` (list): List of NavItem

         **Methods:**
             - `create_nav_items(parent)`: Puts the navigation links in the header.
            - `addItem(item)`: Adds an item of Type NavItem
           - `destroy_item(item)`: Removes an item of Type NavItem


    **Usage:**
        1.  Create a `HeaderNavigationItemsManager`.
        2.  Tell it where to go and how to look (set `root` and `ui_elements`).
        3.  Call `create_nav_items` to show the links.

    **Example:**
         ```python
             header_nav_items = HeaderNavigationItemsManager()
             header_nav_items.root = self.root
             header_nav_items.ui_elements = self.ui_elements
             header_nav_items.create_nav_items(right_section)
         ```
    """
    def __init__(self, ui_elements, root):
        self.root = root
        self.ui_elements = ui_elements
        super().__init__()
        self.items:  List[NavItem] = []
        self.model = NavItemModel(self.ui_elements)

    def addItem(self, item: NavItem):
        if not isinstance(item, NavItem):
           raise ValueError(f"Invalid item type: {type(item)}")
        self.items.append(item)

    def destroy_item(self, item: NavItem):
        if item in self.items:
            self.items.remove(item)

    def create_nav_items(self, parent):
        nav_items = ['Pull requests', 'Issues', 'Marketplace', 'Explore']
        for item in nav_items:
            nav_item = self.model.create_nav_button_item(title=item)
            self.addItem(nav_item)
            if nav_item.type == 'button':
                nav_button = NavButtonItem(master=parent, title=nav_item.title, ui_elements=self.ui_elements)
                nav_button.pack(side="left", padx=4)


class NavButtonItemCreator:
  """
    **Description:**
     Creates different types of navigation items for the header.

    **Methods:**
         - `create_nav_button(title, ui_elements)`: Creates a new NavButton
         - `create_nav_text_item(title, ui_elements)`: Creates a new text based NavItem.

    **Usage:**
        1. Instantiate the `NavButtonItemCreator` class
        2. use one of its creation methods

    **Example:**
         ```python
         creator = NavButtonItemCreator()
         item = creator.create_nav_button(title="Pull requests", ui_elements=self.ui_elements)
         ```
     """
  def create_nav_button(self, title, ui_elements):
    return NavItem(title=title, type='button')
  def create_nav_text_item(self, title, ui_elements):
      return NavItem(title=title, type='text')


class NavigationManager(Manager[NavItem]):
    """
    **Description:**
    Manages the navigation bar.

    Creates the navigation bar at the top, including the repo dropdown and action buttons.

    **Attributes:**
        - `root` (ctk.CTk): The main window to attach it to.
        - `ui_elements` (UIElements): The styling to use.
        - `repo_selector` (RepoSelector): Manages the dropdown selection.
        - `action_buttons` (ActionButtonsManager): Manages the action buttons.
        - `update_repo_callback` (function): Callback for when repo changes.
         - `items` (list): List of NavItem

    **Methods:**
        - `create_navigation()`: Puts all the navigation bar parts together.
         - `addItem(item)`: Adds a new navigation item
          - `destroy_item(item)`: Removes an item of Type NavItem

    **Usage:**
       1.  Create a `NavigationManager`.
       2. Set `root`, `ui_elements` and `update_repo_callback`.
       3. This class manages the creation of the navigation.

    **Example:**
        ```python
        navigation = NavigationManager()
        navigation.root = self.root
        navigation.ui_elements = self.ui_elements
        navigation.update_repo_callback = self.update_repo_dropdown_command
        ```
    """
    def __init__(self, root, ui_elements, update_repo_callback):
        self.root = root
        self.ui_elements = ui_elements
        # Removed repo_selector attribute.
        self.action_buttons = ActionButtonsManager(root, ui_elements)
        self.update_repo_callback = update_repo_callback
        super().__init__()
        self.items : List[NavItem] = []


    def addItem(self, item: NavItem):
        if not isinstance(item, NavItem):
           raise ValueError(f"Invalid item type: {type(item)}")
        self.items.append(item)

    def destroy_item(self, item: NavItem):
          if item in self.items:
              self.items.remove(item)

    def create_navigation(self):
        """Creates the repository-specific navigation bar"""
        nav_bar = ctk.CTkFrame(
            self.root,
            fg_color=self.ui_elements.navbar_color,
            height=50,
            corner_radius=0
        )
        nav_bar.pack(fill="x", pady=(1, 0))
        nav_bar.pack_propagate(False)

        # Repository selector with GitHub styling
        repo_frame = ctk.CTkFrame(nav_bar, fg_color="transparent")
        repo_frame.pack(side="left", padx=16, fill="y")

        #Repo Selector removed, moved to header
        #self.repo_selector.root = self.root
        #self.repo_selector.ui_elements = self.ui_elements
        #self.repo_selector.update_repo_callback = self.update_repo_callback
        #self.repo_selector.create_selector(repo_frame)

        # Action Buttons
        self.action_buttons.root = self.root
        self.action_buttons.ui_elements = self.ui_elements
        self.action_buttons.create_buttons(repo_frame)


class TabBarManager:
    """
    **Description:**
    Creates the tab bar.

    Manages the set of tabs for navigating the content.

    **Attributes:**
        - `root` (ctk.CTk): The main window to attach it to.
        - `ui_elements` (UIElements): The styling to use.
        - `items` (list): List of NavItem

    **Methods:**
         - `create_tab_bar(parent)`: Puts the tabs in the content area.
           - `addItem(item)`: Adds a new navigation item
           - `destroy_item(item)`: Removes an item of type NavItem

    **Usage:**
         1.  Create a `TabBarManager`.
        2.  Tell it where to go and how to look (set `root` and `ui_elements`).
         3. Call `create_tab_bar` to show the tabs.

    **Example:**
         ```python
         tab_bar = TabBarManager()
         tab_bar.root = self.root
         tab_bar.ui_elements = self.ui_elements
         tab_bar.create_tab_bar(self.root)
         ```
    """
    def __init__(self, root, ui_elements):
        self.root = root
        self.ui_elements = ui_elements
        self.items: List[NavItem]= []
        self.model = NavItemModel(self.ui_elements)

    def create_tab_bar(self, parent):
            # Create tab bar with GitHub styling
            tab_frame = ctk.CTkFrame(
                parent,
                fg_color=self.ui_elements.background_color,
                height=50,
                corner_radius=0
            )
            tab_frame.pack(fill="x", pady=(0, 1))


    def addItem(self, item: NavItem):
        if not isinstance(item, NavItem):
           raise ValueError(f"Invalid item type: {type(item)}")
        self.items.append(item)

    def destroy_item(self, item: NavItem):
        if item in self.items:
              self.items.remove(item)

class MainContentFrame:
    """
    **Description:**
     Creates the main area for content.

    Manages the frame that holds the import section and the activity log.

    **Attributes:**
        - `root` (ctk.CTk): The main window to attach it to.
        - `ui_elements` (UIElements): The styling to use.

    **Methods:**
         - `create_main_frame(parent)`: Puts the main frame in the content area.

    **Usage:**
        1.  Create a `MainContentFrame`.
         2.  Tell it where to go and how to look (set `root` and `ui_elements`).
        3.  Call `create_main_frame` to show the main content area.

    **Example:**
         ```python
         main_content_frame = MainContentFrame()
         main_content_frame.root = self.root
         main_content_frame.ui_elements = self.ui_elements
         content_frame = main_content_frame.create_main_frame(self.root)
         ```
    """
    def __init__(self, root, ui_elements):
        self.root = root
        self.ui_elements = ui_elements
    def create_main_frame(self, parent):
        # Main content area
        content_frame = ctk.CTkFrame(
            parent,
            fg_color=self.ui_elements.background_color,
            corner_radius=0
        )
        content_frame.pack(fill="both", expand=True, padx=0, pady=0)
        return content_frame

class ContentAreaManager:
    """
    **Description:**
    Manages the main content section of the application.

    Creates the tab bar and main content area, including import and activity log sections.

    **Attributes:**
        - `root` (ctk.CTk): The main window to attach it to.
        - `ui_elements` (UIElements): The styling settings.
        - `import_section` (ImportSectionManager): Manages the import controls.
        - `activity_log` (ActivityLogManager): Manages the activity log display.
        - `tab_bar` (TabBarManager): Manages the tab bar.
        - `main_content_frame` (MainContentFrame): Manages the main content frame.

    **Methods:**
        - `create_main_content()`: Puts all the content section parts together.

    **Usage:**
        1.  Create a `ContentAreaManager`.
        2. Set `root`, `ui_elements`, `import_section` and `activity_log`.
        3. This class manages the creation of the content area.

    **Example:**
        ```python
        content_area = ContentAreaManager()
        content_area.root = self.root
        content_area.ui_elements = self.ui_elements
        content_area.import_section = self.import_section
        content_area.activity_log = self.activity_log
        ```
    """
    def __init__(self, root, ui_elements, import_section, activity_log):
        self.root = root
        self.ui_elements = ui_elements
        self.import_section = import_section
        self.activity_log = activity_log
        self.tab_bar = TabBarManager(self.root, self.ui_elements)
        self.main_content_frame = MainContentFrame(self.root, self.ui_elements)
        self.create_main_content()

    def create_main_content(self):
        """Creates the main content area with tabs and content"""
        #Tab bar
        self.tab_bar.root = self.root
        self.tab_bar.ui_elements = self.ui_elements
        self.tab_bar.create_tab_bar(self.root)

        #Main Content Frame
        self.main_content_frame.root = self.root
        self.main_content_frame.ui_elements = self.ui_elements
        content_frame = self.main_content_frame.create_main_frame(self.root)


        # Add import controls
        self.import_section.create_import_section(content_frame)

        # Add activity log
        self.activity_log.create_activity_log(content_frame)

class ImportHeaderItem:
    """
    **Description:**
    Creates the import section header.

    Manages the header area of the import section.

    **Attributes:**
         - `root` (ctk.CTk): The main window to attach it to.
         - `ui_elements` (UIElements): The styling to use.

    **Methods:**
         - `create_header(parent)`: Puts the header in the import section.

    **Usage:**
        1. Create a `ImportHeaderItem`.
        2. Set `root` and `ui_elements`.
        3. Call `create_header` to show it in a container.

    **Example:**
         ```python
         import_header = ImportHeaderItem()
         import_header.root = self.root
         import_header.ui_elements = self.ui_elements
         import_header.create_header(import_frame)
         ```
    """
    def __init__(self):
          self.root = None
          self.ui_elements = None
    def create_header(self, parent):
         # Header with icon
        header_frame = ctk.CTkFrame(
            parent,
            fg_color=self.ui_elements.secondary_color,
            height=40,
            corner_radius=6
        )
        header_frame.pack(fill="x")

        header_label = ctk.CTkLabel(
            header_frame,
            text="󰍉 Import Milestones",
            text_color=self.ui_elements.text_color,
            font=("Segoe UI", 14, "bold")
        )
        header_label.pack(side="left", padx=16, pady=8)

class ImportButtonItem:
    def __init__(self, ui_elements, import_callback, github_client, logger):
        self.root = None
        self.ui_elements = ui_elements
        self.import_callback = import_callback
        self.import_button = None
        self.data_importer = DataImporter(github_client, logger)

    def create_button(self, parent):
        self.import_button = ctk.CTkButton(
            parent,
            text="Import Milestones",
            command=self.import_callback,
            fg_color=self.ui_elements.primary_color,
            hover_color=self.ui_elements.primary_hover_color,
            text_color="#FFFFFF",
            font=("Segoe UI", 12),
            height=32,
            corner_radius=6
        )
        self.import_button.pack(side="left", padx=16, pady=16)

    def configure(self, **kwargs):
        if self.import_button:
            self.import_button.configure(**kwargs)

class ImportSectionManager:
    def __init__(self, root, ui_elements, import_callback, github_client, logger):
        self.ui_elements = ui_elements
        self.import_header = ImportHeaderItem()
        self.import_button = ImportButtonItem(self.ui_elements, import_callback, github_client, logger)
        self.root = root
        self.import_callback = import_callback

    def create_import_section(self, parent):
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

        # Import Button
        self.import_button.root = self.root
        self.import_button.create_button(import_frame)

class ActivityLogHeaderItem:
    """
    **Description:**
    Manages the header of the ActivityLog section.

    **Attributes:**
        - `root` (ctk.CTk): Root window for widgets.
        - `ui_elements` (UIElements): Styling attributes.

    **Methods:**
        - `create_header(parent)`: Creates the header.

    **Usage:**
        Instantiate `ActivityLogHeaderItem`, set `root` and `ui_elements`, then use `create_header`.

    **Example:**
         ```python
         activity_log_header = ActivityLogHeaderItem()
         activity_log_header.root = self.root
         activity_log_header.ui_elements = self.ui_elements
         activity_log_header.create_header(log_frame)
         ```
    """
    def __init__(self):
          self.root = None
          self.ui_elements = None
    def create_header(self, parent):
        # Header with icon
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

@dataclass
class ActivityLogItem:
    timestamp: str
    icon: str
    msg: str
    level: str = 'info'

class ActivityLogTextItem(ctk.CTkTextbox):
    def __init__(self, master, ui_elements, **kwargs):
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

    def _format_log(self, timestamp, icon, msg):
        self.insert('end', f"{timestamp} ", ('timestamp',))
        self.insert('end', f"{icon} ", ('icon',))
        self.insert('end', f"{msg}\n", ('message',))

        self.tag_config('timestamp', foreground=self.ui_elements.text_secondary_color)
        self.tag_config('icon', foreground=self.ui_elements.text_color)
        self.tag_config('message', foreground=self.ui_elements.text_color)

class ActivityLogManager(Manager[ActivityLogItem]):
    """
     **Description:**
    Manages the Activity Log section.

    Creates the Activity Log section, including header and text area.
     **Attributes:**
        - `ui_elements` (UIElements): Instance of the UIElements for consistent styling.
        - `textbox_logger` (TextboxLogger): instance of TextboxLogger for handling the logs.
        - `header` (ActivityLogHeaderItem): The Activity Log header item
         -  `items` (list): List of ActivityLogItem

    **Methods:**
        - `addItem(item)`: Adds Activity Log item.
       - `create_activity_log(parent)`: Creates the full activity log UI.
        - `log_handler(record)`: Handles log messages.
         -  `destroy_item(item)`: Removes an item of type ActivityLogItem.

    **Usage:**
        1.  Create a `ActivityLogManager`.
        2. Set `ui_elements` and `textbox_logger`.
       3. Call `create_activity_log` to show the activity log area.
        4. Use addItem to add different log messages.

    **Example:**
        ```python
        activity_log = ActivityLogManager()
        activity_log.ui_elements = self.ui_elements
        activity_log.textbox_logger = self.textbox_logger
         activity_log.create_activity_log(content_frame)
        ```
    """
    def __init__(self, ui_elements, textbox_logger, root):
        self.ui_elements = ui_elements
        self.textbox_logger = textbox_logger
        self.header = ActivityLogHeaderItem()
        self.root = root
        super().__init__()

    def create_activity_log(self, parent):
        """Creates GitHub-style activity log section"""
        log_frame = ctk.CTkFrame(
            parent,
            fg_color=self.ui_elements.surface_color,
            corner_radius=6
        )
        log_frame.pack(fill="both", expand=True)

        #Activity Log Header
        self.header.root = self.root
        self.header.ui_elements = self.ui_elements
        self.header.create_header(log_frame)
        # Activity log text area
        # Set the textbox on the logger
        if self.items:
             self.textbox_logger.textbox = self.items[0]
        else:
             activity_log_text_item = ActivityLogTextItem(parent, self.ui_elements)
             activity_log_text_item.pack(fill="both", expand=True, padx=16, pady=16)
             self.textbox_logger.textbox = activity_log_text_item
             self.items.append(activity_log_text_item)



    def addItem(self, item: ActivityLogItem):
        if not isinstance(item, ActivityLogItem):
           raise ValueError(f"Invalid item type: {type(item)}")

        if self.items:
            self.items[0]._format_log(item.timestamp, item.icon, item.msg)

    def destroy_item(self, item: ActivityLogItem):
         if item in self.items:
            self.items.remove(item)


    def log_handler(self, record):
      """handles log messages and passes them to the logger"""
      timestamp = record.created.strftime("%H:%M:%S")

        # GitHub-style status icons
      level_icons = {
            'INFO': '󰆼',  # Check circle
            'ERROR': '󰅚',  # X circle
            'WARNING': '󰀦',  # Warning triangle
           'DEBUG' :  '󰌄'
        }
      icon = level_icons.get(record.levelname, '')
      log_item =  ActivityLogModel().createActivityLogItem(timestamp=timestamp, icon=icon, msg=record.msg, level=record.levelname)
      self.addItem(log_item)
      self.textbox_logger.emit(record)

class ActivityLogModel:
    """
    **Description:**
    Creates custom Activity log items.

    Manages custom Activity log entries.

    **Methods:**
         - `createActivityLogItem(timestamp, icon, msg)`: Creates a new activity log item

     **Usage:**
        1. Instantiate the `ActivityLogModel` class.
        2. Use its `createActivityLogItem` to create log entries.

    **Example:**
        ```python
         creator = ActivityLogModel()
         item = creator.createActivityLogItem("timestamp", "󰅚", "failed to load")
        ```
    """

    def createActivityLogItem(self, timestamp, icon, msg, level='info'):
        return ActivityLogItem(timestamp=timestamp, icon=icon, msg=msg, level=level)


class RepoSelector:
    """
    **Description:**
    Creates a dropdown menu for selecting a repository.

    Manages the dropdown for selecting the repo.

    **Attributes:**
         - `root` (ctk.CTk): The main window to attach it to.
         - `ui_elements` (UIElements): The styling to use.
         - `repo_selection` (ctk.StringVar):  Keeps track of which repo is chosen.
         - `repo_dropdown` (ctk.CTkOptionMenu):  The actual dropdown menu.
         - `update_repo_callback` (function): Callback for when repo changes.

    **Methods:**
         - `create_selector(parent)`: Puts the dropdown menu in the navigation bar.

    **Usage:**
        1. Create a `RepoSelector`.
        2. Set `root`, `ui_elements`, and `update_repo_callback`.
        3. Call `create_selector` to show it in a container.

    **Example:**
         ```python
         repo_selector = RepoSelector()
         repo_selector.root = self.root
         repo_selector.ui_elements = self.ui_elements
         repo_selector.update_repo_callback = self.update_repo_dropdown_command
         repo_selector.create_selector(repo_frame)
         ```
    """

    def __init__(self, root, ui_elements, update_repo_callback):
        self.root = root
        self.ui_elements = ui_elements
        self.repo_selection = ctk.StringVar()
        self.repo_dropdown = None
        self.update_repo_callback = update_repo_callback

    def create_selector(self, parent):
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

class ActionButtonsManager:
    """
    **Description:**
    Creates "Watch", "Fork", and "Star" buttons.

    Manages the action buttons on the navigation bar.

    **Attributes:**
        - `root` (ctk.CTk): The main window to attach them to.
        - `ui_elements` (UIElements): The styling to use.

    **Methods:**
        - `create_buttons(parent)`: Puts the action buttons on the navigation bar.

    **Usage:**
        1.  Create an `ActionButtonsManager`.
        2.  Tell it where to go and how to look (set `root` and `ui_elements`).
        3.  Call `create_buttons` to display the action buttons.

    **Example:**
         ```python
             action_buttons = ActionButtonsManager()
             action_buttons.root = self.root
             action_buttons.ui_elements = self.ui_elements
             action_buttons.create_buttons(repo_frame)
         ```
    """
    def __init__(self, root, ui_elements):
        self.root = root
        self.ui_elements = ui_elements
    def create_buttons(self, parent):
          # Watch, Fork, Star buttons (GitHub-style)
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

# In HeaderManager class
class HeaderManager:
    def __init__(self, root, ui_elements, update_repo_callback): # Added update_repo_callback
        self.root = root
        self.ui_elements = ui_elements
        self.header_logo = HeaderLogoItem()
        self.header_search = HeaderSearchItem()
        self.header_nav_items = HeaderNavigationItemsManager(self.ui_elements, self.root)
        # Added repo selector as class attribute
        self.repo_selector = RepoSelector(self.root, self.ui_elements, update_repo_callback) # Added update_repo_callback
        self.create_header()


    def create_header(self):
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

       # GitHub-style layout with flex-like positioning
       # Left section - Logo and search
       left_section = ctk.CTkFrame(header, fg_color="transparent")
       left_section.pack(side="left", padx=16, fill="y")

       #Header Logo
       self.header_logo.root = self.root
       self.header_logo.ui_elements = self.ui_elements
       self.header_logo.create_logo(left_section)

       # Repo Selector - Moved here
       self.repo_selector.create_selector(left_section)

       #Header Search
       self.header_search.root = self.root
       self.header_search.ui_elements = self.ui_elements
       self.header_search.create_search(left_section)

       # Right section - Navigation items
       right_section = ctk.CTkFrame(header, fg_color="transparent")
       right_section.pack(side="right", padx=16, fill="y")

       #Header Nav Items
       self.header_nav_items.root = self.root
       self.header_nav_items.ui_elements = self.ui_elements
       self.header_nav_items.create_nav_items(right_section)

class HeaderLogoItem:
    """
     **Description:**
    Creates the logo in the header.

    Manages the logo area at the top of the app.

     **Attributes:**
        - `root` (ctk.CTk): The main window to attach it to.
        - `ui_elements` (UIElements): The styling to use.

    **Methods:**
        - `create_logo(parent)`: Puts the logo on the header.

    **Usage:**
        1.  Create a `HeaderLogoItem`.
        2.  Tell it where to go and how to look (set `root` and `ui_elements`).
        3.  Call `create_logo` to show it in a container.

    **Example:**
         ```python
         header_logo = HeaderLogoItem()
         header_logo.root = self.root
         header_logo.ui_elements = self.ui_elements
         header_logo.create_logo(left_section)
         ```
    """
    def __init__(self):
        self.root = None
        self.ui_elements = None
    def create_logo(self, parent):
         # GitHub "Octocat" logo placeholder
        logo_label = ctk.CTkLabel(
            parent,
            text="Github Planner",  # Octocat-like symbol
            text_color=self.ui_elements.text_color,
            font=("Segoe UI", 24)
        )
        logo_label.pack(side="left", padx=(0, 16))

class HeaderSearchItem:
    """
     **Description:**
    Creates the search bar in the header.

    Manages the area where users can search or jump to specific areas.

        **Attributes:**
             - `root` (ctk.CTk): The main window to attach it to.
             - `ui_elements` (UIElements): The styling to use.

        **Methods:**
             - `create_search(parent)`: Puts the search bar in the header.

        **Usage:**
            1.  Create a `HeaderSearchItem`.
            2.  Tell it where to go and how to look (set `root` and `ui_elements`).
            3.  Call `create_search` to show it in a container.

        **Example:**
         ```python
             header_search = HeaderSearchItem()
             header_search.root = self.root
             header_search.ui_elements = self.ui_elements
             header_search.create_search(left_section)
         ```
     """
    def __init__(self):
        self.root = None
        self.ui_elements = None
    def create_search(self, parent):
         # Search bar with GitHub styling
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

class StatusInterface:
    """
    **Description:**
    A status interface to handle status updates with GitHub-style notifications.

    This class abstracts the process of handling status updates, allowing
    the application to maintain compatibility with code that expects a status
    label, while displaying status updates as GitHub-style notifications.

    **Attributes:**
        - `main_window` (MainWindow): A reference to the main application window.
        - `notification_manager` (NotificationManager): The notification manager class.
        - `config` (dict): Configuration settings for the status interface.
    """
    def __init__(self, main_window, notification_manager):
        """
        Initializes the status interface.

        Args:
            main_window (MainWindow): A reference to the main application window.
            notification_manager (NotificationManager): The notification manager class.
        """
        self.main_window = main_window
        self.notification_manager = notification_manager
        self.config = {}

    def update(self, message, level='info'):
        """
        Handles status updates and displays them as GitHub-style notifications.

        Determines the type of notification based on the content of the message
        (e.g., error, success, info) and displays it accordingly.

        Args:
            message (str): The status message.
            level (str): The type of notification (error, success, info)
        """
        # Log the message
        if level == 'error':
            self.main_window.logger.error(message)
        else:
            self.main_window.logger.info(message)

        # Show in the activity log
        log_item = ActivityLogModel().createActivityLogItem(timestamp='', icon='', msg=message, level=level)
        self.main_window.activity_log.addItem(log_item)

        # Show notification
        item = NotificationModel().createNotificationItem(title=level.capitalize(), message=message, level=level)
        self.notification_manager.addItem(item)

class MainWindow:
    """
    The main application window for the GitHub Milestones Importer.

    This class sets up the main GUI using customtkinter, following GitHub's
    design guidelines. It manages the overall structure and interactions between the feature classes
    and performs application level actions like updating repositories, import milestones and exiting the application.

    Attributes:
        root (ctk.CTk): The main application window.
        logger (Logger): The application's logger instance.
        github_client (GitHubClient): An instance of the GitHub client for API interactions.
        auth_gui (AuthGUI): The authentication GUI instance.
        import_gui (ImportGUI): The import GUI instance.
        ui_elements (UIElements): Instance of the UIElements class for consistent styling.
        header (HeaderManager): Instance of the HeaderManager class.
        navigation (NavigationManager): Instance of the NavigationManager class.
        content_area (ContentAreaManager): Instance of the ContentAreaManager class.
        import_section (ImportSectionManager): Instance of the ImportSectionManager class.
        activity_log (ActivityLogManager): Instance of the ActivityLogManager class.
        status_interface (StatusInterface): Handles status updates and messages
    """

    def __init__(self, auth_gui, github_client, import_gui, logger):
        """Initializes the main window with necessary GUI components, logger and other components.

        Args:
            auth_gui (AuthGUI): The authentication GUI instance.
            github_client (GitHubClient): An instance of the GitHub client for API interactions.
            import_gui (ImportGUI): The import GUI instance.
            logger (Logger): The application's logger instance.
        """

        self.logger = logger
        self.auth_manager = AuthManager(Config(),logger)
        self.github_client2 = GitHubClient(TokenStorage().load_tokens()[0],logger,self.auth_manager)
        self.data_importer = DataImporter(github_client, logger)
        self.root = ctk.CTk()
        self.root.title("GitHub Milestones Importer")
        self.auth_gui = auth_gui
        self.import_gui = import_gui

        # UI elements
        self.ui_elements = UIElements()
        self.notification_manager = NotificationManager(self.root, self.ui_elements)
        self.textbox_logger = TextboxLogger(self.ui_elements)
        self.status_interface = StatusInterface(self, self.notification_manager)

        # Setup UI components
        self.activity_log = ActivityLogManager(self.ui_elements, self.textbox_logger, self.root)
        self.import_section = ImportSectionManager(self.root, self.ui_elements, self.import_milestones,
                                                   self.github_client2, self.logger)
        self.navigation = NavigationManager(self.root, self.ui_elements, self.update_repo_dropdown_command)
        self.header = HeaderManager(self.root, self.ui_elements, self.update_repo_dropdown_command)
        self.content_area = ContentAreaManager(self.root, self.ui_elements, self.import_section,
                                               self.activity_log)

        # Initialize events
        self.logger.addHandler(self.textbox_logger)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # Ensure repo_selector is created before updating the dropdown
        self.update_repo_dropdown()

        # Initialize repo_selection attribute
        self.repo_selection = self.header.repo_selector.repo_selection

        # Initialize DataImporter with required arguments
        self.import_section.import_button.import_button.configure(state='disabled')

    def update_repo_dropdown_command(self, selected_repo):
        """
        Command to execute when a repository is selected
        """
        if selected_repo:
            self._enable_import_button()

    def create_milestone(self, milestone):
        """
        Creates a milestone in the selected repository.
        """
        # try:
        self.github_client2.create_milestone(milestone)
        self.status_interface.update(f"Milestone {milestone['title']} created", level='info')
        # except Exception as e:
        #     self.logger.error(f"Failed to create milestone: {e}")
        #     self.status_interface.update(f"Error: {e}", level='error')

    def update_repo_dropdown(self):
        """
        Updates the repository selector with available GitHub repositories.
        This method mirrors GitHub's repository navigation behavior, including
        loading states and error handling patterns.
        """
        if self.github_client2:
            try:
                # Retrieve repositories from GitHub
                repos = self.github_client2.get_user_repos()

                # Format repositories in GitHub's owner/repo style with organization icons
                repo_list = []
                for repo in repos:
                    owner = repo['owner']['login']
                    name = repo['name']
                    # Add organization/user icon based on repo type
                    icon = '󰒋' if repo['owner']['type'] == 'Organization' else '󰀄'
                    repo_list.append(f"{icon} {owner}/{name}")

                # Update dropdown with GitHub styling
                self.header.repo_selector.repo_dropdown.configure(
                    values=repo_list,
                    state="normal",
                    dropdown_fg_color=self.ui_elements.surface_color,
                    dropdown_text_color=self.ui_elements.text_color,
                    text_color=self.ui_elements.text_color
                )
            except Exception as e:
                self.logger.error(f"Failed to update repo dropdown: {e}")
                self.status_interface.update(f"Error: {e}", level='error')


    def _enable_import_button(self, *args):
        """
        Manages the import button state following GitHub's button behavior patterns.
        Includes proper visual feedback and state management.
        """
        if self.header.repo_selector.repo_selection.get():
            # Enable with GitHub's primary button styling
            self.import_section.import_button.configure(
                state="normal",
                fg_color=self.ui_elements.primary_color,
                hover_color=self.ui_elements.primary_hover_color,
                text="Import Milestones"
            )
        else:
            # Disable with GitHub's disabled button styling
            self.import_section.import_button.configure(
                state="disabled",
                fg_color=self.ui_elements.secondary_color,
                hover_color=self.ui_elements.secondary_hover_color,
                text="Select a repository"
            )

    def import_milestones(self):
        """
        Imports milestones from the selected repository.
        """
        # try:
        # Extract repo_owner and repo_name from the selected repository
        selected_repo = self.repo_selection.get().split("/")
        user_name = selected_repo[0][2:].strip()
        repo_name = selected_repo[1].strip()
        # Perform the import operation
        file_path = self.open_file_dialog()
        self.data_importer.import_data(file_path, user_name, repo_name)
        # Update the import button state
        self.import_section.import_button.import_button.configure(state='disabled')

        # except Exception as e:
        #     self.logger.error(f"Failed to import milestones: {e}")
        #     self.status_interface.update(f"Error: {e}", level='error')

    def open_file_dialog(self):
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Select a JSON file"
        )
        return file_path

    def on_close(self):
        """
        Handles application closure with GitHub-style confirmation.
        """
        if ctk.CTkMessagebox.askokcancel(
                "Close GitHub Milestones Importer",
                "Are you sure you want to close the importer?",
                icon='warning'
        ):
            self.logger.info("Closing GitHub Milestones Importer")
            self.root.destroy()

    def run(self):
        """
        Initializes and runs the main application window.
        Sets up the window with proper positioning and scaling.
        """
        # Center window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Use GitHub-like default window size
        window_width = 800
        window_height = 600

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Position window and start application
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.mainloop()

def main():
    logger = Logger("github_importer")
    root = MainWindow(None, None, None, logger)
    root.run()

if __name__ == "__main__":
    main()