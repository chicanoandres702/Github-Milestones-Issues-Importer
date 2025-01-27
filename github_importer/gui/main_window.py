import customtkinter as ctk
from tkinter import scrolledtext, messagebox
from github_importer.utils.logger import Logger


class MainWindow:
    def __init__(self, auth_gui, github_client, import_gui, logger):
        self.root = ctk.CTk()
        self.root.title("GitHub Milestones Importer")
        self.logger = logger
        self.github_client = github_client
        self.auth_gui = auth_gui
        self.import_gui = import_gui

        # Add this line to create the status interface
        self.status_interface = self._create_status_interface()

        # GitHub's exact color palette
        self.colors = {
            'background': "#0D1117",  # Main background
            'surface': "#161B22",  # Surface/card background
            'header': "#010409",  # Header background
            'primary': "#2EA043",  # Primary button
            'primary_hover': "#3FB950",  # Primary button hover
            'secondary': "#21262D",  # Secondary button
            'secondary_hover': "#30363D",  # Secondary button hover
            'border': "#30363D",  # Borders
            'text': "#C9D1D9",  # Primary text
            'text_secondary': "#8B949E",  # Secondary text
            'accent': "#58A6FF",  # Links and accents
            'error': "#F85149",  # Error states
            'success': "#2EA043",  # Success states
            'tab_active': "#1F6FEB",  # Active tab indicator
            'navbar': "#161B22",  # Navigation bar
            'counter_bg': "#30363D",  # Badge/counter background
            'dropdown_hover': "#1F6FEB"  # Dropdown hover state
        }

        # Window Setup
        self.root.configure(fg_color=self.colors['background'])
        self.root.geometry("1200x800")  # Larger window for GitHub-like layout

        # Create main layout
        self.create_header()
        self.create_navigation()
        self.create_main_content()

        # Initialize events
        self.logger.addHandler(self.log_handler)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.update_repo_dropdown()

    def _create_status_interface(self):
        """
        Creates a status interface that maintains compatibility with code expecting a status label
        while providing GitHub-style notifications
        """

        class StatusInterface:
            def __init__(self, main_window):
                self.main_window = main_window

            def configure(self, **kwargs):
                """Handles status updates in a GitHub-style way"""
                if 'text' in kwargs:
                    message = kwargs['text']
                    # Determine notification type based on message content
                    level = 'info'
                    if any(word in message.lower() for word in ['error', 'failed', 'invalid']):
                        level = 'error'
                    elif any(word in message.lower() for word in ['success', 'completed', 'retrieved']):
                        level = 'success'

                    # Log the message
                    if level == 'error':
                        self.main_window.logger.error(message)
                    else:
                        self.main_window.logger.info(message)

                    # Show in the activity log
                    self.main_window.log_handler({'level': level, 'msg': message})

        return StatusInterface(self)

    def create_header(self):
        """Creates GitHub's top header with navigation and user controls"""
        # Main header bar
        header = ctk.CTkFrame(
            self.root,
            fg_color=self.colors['header'],
            height=60,
            corner_radius=0
        )
        header.pack(fill="x", pady=0)
        header.pack_propagate(False)

        # GitHub-style layout with flex-like positioning
        # Left section - Logo and search
        left_section = ctk.CTkFrame(header, fg_color="transparent")
        left_section.pack(side="left", padx=16, fill="y")

        # GitHub "Octocat" logo placeholder
        logo_label = ctk.CTkLabel(
            left_section,
            text="󰊤",  # Octocat-like symbol
            text_color=self.colors['text'],
            font=("Segoe UI", 24)
        )
        logo_label.pack(side="left", padx=(0, 16))

        # Search bar with GitHub styling
        search_frame = ctk.CTkFrame(
            left_section,
            fg_color=self.colors['background'],
            height=28,
            corner_radius=6
        )
        search_frame.pack(side="left", padx=8)

        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search or jump to...",
            text_color=self.colors['text'],
            fg_color="transparent",
            border_width=0,
            height=28,
            width=240
        )
        search_entry.pack(side="left", padx=8)

        # Right section - Navigation items
        right_section = ctk.CTkFrame(header, fg_color="transparent")
        right_section.pack(side="right", padx=16, fill="y")

        # GitHub-style navigation items
        nav_items = ["Pull requests", "Issues", "Marketplace", "Explore"]
        for item in nav_items:
            nav_button = ctk.CTkButton(
                right_section,
                text=item,
                fg_color="transparent",
                hover_color=self.colors['surface'],
                text_color=self.colors['text'],
                height=32,
                corner_radius=4
            )
            nav_button.pack(side="left", padx=4)

    def create_navigation(self):
        """Creates the repository-specific navigation bar"""
        nav_bar = ctk.CTkFrame(
            self.root,
            fg_color=self.colors['navbar'],
            height=50,
            corner_radius=0
        )
        nav_bar.pack(fill="x", pady=(1, 0))
        nav_bar.pack_propagate(False)

        # Repository selector with GitHub styling
        self.repo_selection = ctk.StringVar()
        repo_frame = ctk.CTkFrame(nav_bar, fg_color="transparent")
        repo_frame.pack(side="left", padx=16, fill="y")

        # Repository dropdown with GitHub's book icon
        self.repo_dropdown = ctk.CTkOptionMenu(
            repo_frame,
            variable=self.repo_selection,
            # fg_color="transparent",
            button_color=self.colors['secondary'],
            button_hover_color=self.colors['secondary_hover'],
            text_color=self.colors['text'],
            dropdown_fg_color=self.colors['surface'],
            dropdown_hover_color=self.colors['dropdown_hover'],
            dropdown_text_color=self.colors['text'],
            width=300,
            height=32,
            corner_radius=6,
            font=("Segoe UI", 12),
            dynamic_resizing=False
        )
        self.repo_dropdown.pack(side="left", padx=(0, 8))

        # Watch, Fork, Star buttons (GitHub-style)
        for action in [("󰯈 Watch", "12"), ("󰘖 Fork", "5"), ("󰓎 Star", "23")]:
            btn_frame = ctk.CTkFrame(
                repo_frame,
                fg_color=self.colors['secondary'],
                corner_radius=6,
                height=32
            )
            btn_frame.pack(side="left", padx=4)
            btn_frame.pack_propagate(False)

            btn = ctk.CTkButton(
                btn_frame,
                text=action[0],
                fg_color="transparent",
                hover_color=self.colors['secondary_hover'],
                text_color=self.colors['text'],
                height=32,
                corner_radius=6,
                font=("Segoe UI", 12)
            )
            btn.pack(side="left", padx=8)

            # Counter badge
            counter = ctk.CTkLabel(
                btn_frame,
                text=action[1],
                fg_color=self.colors['counter_bg'],
                text_color=self.colors['text'],
                corner_radius=10,
                font=("Segoe UI", 11),
                width=30,
                height=20
            )
            counter.pack(side="right", padx=8)

    def create_main_content(self):
        """Creates the main content area with tabs and content"""
        # Create tab bar with GitHub styling
        tab_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors['background'],
            height=50,
            corner_radius=0
        )
        tab_frame.pack(fill="x", pady=(0, 1))

        # GitHub-style tabs with icons and counters
        tabs = [
            ("󰈙 Code", ""),
            ("◎ Issues", "12"),
            ("󰓼 Pull requests", "4"),
            ("󰟜 Actions", ""),
            ("󰼏 Projects", "2"),
            ("󰏗 Wiki", ""),
            ("󰋗 Security", ""),
            ("󰧮 Insights", ""),
            ("⚙️ Settings", "")
        ]

        for i, (tab_text, count) in enumerate(tabs):
            tab_button = ctk.CTkButton(
                tab_frame,
                text=tab_text + (f" {count}" if count else ""),
                fg_color="transparent",
                hover_color=self.colors['surface'],
                text_color=self.colors['text'],
                height=48,
                corner_radius=0,
                font=("Segoe UI", 12)
            )
            tab_button.pack(side="left", padx=8)

            # Active tab indicator
            if i == 0:  # Code tab is active
                indicator = ctk.CTkFrame(
                    tab_frame,
                    fg_color=self.colors['tab_active'],
                    height=2,
                    corner_radius=0
                )
                indicator.place(relx=0.04, rely=0.96, relwidth=0.08)

        # Main content area
        content_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors['background'],
            corner_radius=0
        )
        content_frame.pack(fill="both", expand=True, padx=24, pady=24)

        # Add import controls
        self.create_import_section(content_frame)

        # Add activity log
        self.create_activity_log(content_frame)

    def create_import_section(self, parent):
        """Creates the import controls section with GitHub styling"""
        import_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors['surface'],
            corner_radius=6
        )
        import_frame.pack(fill="x", pady=(0, 16))

        # Header with icon
        header_frame = ctk.CTkFrame(
            import_frame,
            fg_color=self.colors['secondary'],
            height=40,
            corner_radius=6
        )
        header_frame.pack(fill="x")

        header_label = ctk.CTkLabel(
            header_frame,
            text="󰍉 Import Milestones",
            text_color=self.colors['text'],
            font=("Segoe UI", 14, "bold")
        )
        header_label.pack(side="left", padx=16, pady=8)

        # Import button
        self.import_button = ctk.CTkButton(
            import_frame,
            text="Import Milestones",
            command=self.import_milestones,
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_hover'],
            text_color="#FFFFFF",
            font=("Segoe UI", 12),
            height=32,
            corner_radius=6
        )
        self.import_button.pack(side="left", padx=16, pady=16)

    def create_activity_log(self, parent):
        """Creates GitHub-style activity log section"""
        log_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors['surface'],
            corner_radius=6
        )
        log_frame.pack(fill="both", expand=True)

        # Header with icon
        header_frame = ctk.CTkFrame(
            log_frame,
            fg_color=self.colors['secondary'],
            height=40,
            corner_radius=6
        )
        header_frame.pack(fill="x")

        header_label = ctk.CTkLabel(
            header_frame,
            text="󰑍 Activity",
            text_color=self.colors['text'],
            font=("Segoe UI", 14, "bold")
        )
        header_label.pack(side="left", padx=16, pady=8)

        # Activity log text area
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap="word",
            bg=self.colors['background'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            font=("Segoe UI", 11),
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=self.colors['border'],
            relief="flat"
        )
        self.log_text.pack(fill="both", expand=True, padx=16, pady=16)

    def log_handler(self, record):
        """Handles log messages with GitHub-style formatting"""
        self.log_text.configure(state='normal')

        timestamp = record.created.strftime("%H:%M:%S")

        # GitHub-style status icons
        level_icons = {
            'INFO': '󰆼',  # Check circle
            'ERROR': '󰅚',  # X circle
            'WARNING': '󰀦'  # Warning triangle
        }

        level_colors = {
            'INFO': self.colors['success'],
            'ERROR': self.colors['error'],
            'WARNING': '#D29922'  # GitHub warning color
        }

        icon = level_icons.get(record.levelname, '')
        color = level_colors.get(record.levelname, self.colors['text'])

        # Insert GitHub-style log entry
        self.log_text.insert('end', f"{timestamp} ", ('timestamp',))
        self.log_text.insert('end', f"{icon} ", ('icon',))
        self.log_text.insert('end', f"{record.msg}\n", ('message',))

        # Apply GitHub-style formatting
        self.log_text.tag_config('timestamp', foreground=self.colors['text_secondary'])
        self.log_text.tag_config('icon', foreground=color)
        self.log_text.tag_config('message', foreground=self.colors['text'])

        self.log_text.see('end')
        self.log_text.configure(state='disabled')

    def update_repo_dropdown(self):
        """
        Updates the repository selector with available GitHub repositories.
        This method mirrors GitHub's repository navigation behavior, including
        loading states and error handling patterns.
        """
        if self.github_client:
            try:
                # Show GitHub-style loading state
                self.repo_dropdown.configure(
                    state="disabled",
                    text="Loading repositories..."
                )

                # Fetch repositories through GitHub API
                repos = self.github_client.get_user_repos()

                # Format repositories in GitHub's owner/repo style with organization icons
                repo_list = []
                for repo in repos:
                    owner = repo['owner']['login']
                    name = repo['name']
                    # Add organization/user icon based on repo type
                    icon = '󰒋' if repo['owner']['type'] == 'Organization' else '󰀄'
                    repo_list.append(f"{icon} {owner}/{name}")

                # Update dropdown with GitHub styling
                self.repo_dropdown.configure(
                    values=repo_list,
                    state="normal",
                    dropdown_fg_color=self.colors['surface'],
                    dropdown_text_color=self.colors['text'],
                    text_color=self.colors['text']
                )

                # Select first repository by default (GitHub behavior)
                if repo_list:
                    self.repo_selection.set(repo_list[0])
                    self._enable_import_button()

                    # Log success with GitHub-style success icon
                    self.logger.info(f"Found {len(repo_list)} repositories")

            except Exception as e:
                # Show GitHub-style error state
                error_message = f"Could not load repositories: {str(e)}"
                self.repo_dropdown.configure(
                    state="normal",
                    text="Error loading repositories"
                )
                self.logger.error(error_message)

                # Show GitHub-style error notification
                self._show_notification(
                    "Error",
                    error_message,
                    level="error"
                )

    def _enable_import_button(self, *args):
        """
        Manages the import button state following GitHub's button behavior patterns.
        Includes proper visual feedback and state management.
        """
        if self.repo_selection.get():
            # Enable with GitHub's primary button styling
            self.import_button.configure(
                state="normal",
                fg_color=self.colors['primary'],
                hover_color=self.colors['primary_hover'],
                text="Import Milestones"
            )
        else:
            # Disable with GitHub's disabled button styling
            self.import_button.configure(
                state="disabled",
                fg_color=self.colors['secondary'],
                hover_color=self.colors['secondary'],
                text="Select a repository"
            )

    def import_milestones(self):
        """
        Handles the milestone import process with GitHub's progress indicators
        and notification patterns. Provides clear visual feedback throughout
        the import operation.
        """
        selected_repo = self.repo_selection.get()
        if not selected_repo:
            self._show_notification(
                "Error",
                "Please select a repository first",
                level="error"
            )
            return

        # Extract actual repo name from formatted string
        repo_name = selected_repo.split(" ", 1)[1]  # Remove icon prefix

        try:
            # Show GitHub-style loading state
            self.import_button.configure(
                state="disabled",
                text="Importing...",
                fg_color=self.colors['secondary']
            )

            # Add loading indicator to log
            self.logger.info(f"Starting import for {repo_name}")

            # Perform the import
            self.import_gui.run(repo_name)

            # Show success notification
            self._show_notification(
                "Success",
                f"Successfully imported milestones for {repo_name}",
                level="success"
            )

            self.logger.info(f"Successfully imported milestones for {repo_name}")

        except Exception as e:
            # Show error notification
            error_message = f"Failed to import milestones: {str(e)}"
            self._show_notification(
                "Error",
                error_message,
                level="error"
            )
            self.logger.error(error_message)

        finally:
            # Reset button state
            self.import_button.configure(
                state="normal",
                text="Import Milestones",
                fg_color=self.colors['primary']
            )

    def _show_notification(self, title, message, level="info"):
        """
        Displays GitHub-style notifications for user feedback.
        Creates a temporary overlay notification that matches GitHub's design.
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
            "success": self.colors['success'],
            "error": self.colors['error'],
            "info": self.colors['secondary']
        }.get(level, self.colors['secondary'])

        # Create notification content
        frame = ctk.CTkFrame(
            notification,
            fg_color=self.colors['surface'],
            corner_radius=6,
            border_width=1,
            border_color=self.colors['border']
        )
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Add icon based on notification type
        icon = {
            "success": "󰄬",  # Checkmark
            "error": "󰅚",  # X mark
            "info": "󰋼"  # Info icon
        }.get(level, "󰋼")

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
            text=title,
            text_color=self.colors['text'],
            font=("Segoe UI", 12, "bold")
        )
        title_label.pack(anchor="w")

        message_label = ctk.CTkLabel(
            text_frame,
            text=message,
            text_color=self.colors['text_secondary'],
            font=("Segoe UI", 11)
        )
        message_label.pack(anchor="w")

        # Auto-close notification after 3 seconds
        notification.after(3000, notification.destroy)

    def on_close(self):
        """
        Handles application closure with GitHub-style confirmation.
        """
        if messagebox.askokcancel(
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
        window_width = 1200
        window_height = 800

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Position window and start application
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.mainloop()