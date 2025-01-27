import customtkinter as ctk
from tkinter import scrolledtext, messagebox
from github_importer.utils.logger import Logger


class MainWindow:
    def __init__(self, auth_gui, github_client, import_gui, logger):
        # Initialize the root window with modern styling
        self.root = ctk.CTk()
        self.root.title("GitHub Milestones Importer")
        self.logger = logger
        self.github_client = github_client
        self.auth_gui = auth_gui
        self.import_gui = import_gui

        # Modern Dark Theme Color Palette
        # Using a carefully chosen set of colors that work together harmoniously
        self.colors = {
            'background': "#1E1E2E",  # Rich dark background
            'surface': "#2A2A3C",  # Slightly lighter for cards
            'primary': "#7C3AED",  # Vibrant purple for primary actions
            'primary_hover': "#8B5CF6",  # Lighter purple for hover states
            'text': "#E2E8F0",  # Soft white for main text
            'text_secondary': "#94A3B8",  # Muted color for secondary text
            'border': "#313244",  # Subtle borders
            'error': "#EF4444",  # Red for errors
            'success': "#10B981"  # Green for success states
        }

        # Window Setup with larger default size
        self.root.configure(fg_color=self.colors['background'])
        self.root.geometry("900x650")

        # Main Container with rounded corners and padding
        self.main_container = ctk.CTkFrame(
            self.root,
            fg_color=self.colors['background'],
            corner_radius=20,
        )
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header Section
        self.create_header_section()

        # Repository Selection Section
        self.create_repo_section()

        # Logging Section
        self.create_log_section()

        # Status Bar
        self.create_status_bar()

        # Initialize logging and window events
        self.logger.addHandler(self.log_handler)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.repo_selection.trace("w", self._enable_import_button)
        self.update_repo_dropdown()

    def create_header_section(self):
        """Creates the header section with title and description"""
        header_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent",
            height=60
        )
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="GitHub Milestones Importer",
            text_color=self.colors['text'],
            font=("Inter", 24, "bold"),
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Import and manage your GitHub milestones efficiently",
            text_color=self.colors['text_secondary'],
            font=("Inter", 12),
        )
        subtitle.pack(anchor="w")

    def create_repo_section(self):
        """Creates the repository selection section with modern styling"""
        repo_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=self.colors['surface'],
            corner_radius=15,
            height=80
        )
        repo_frame.pack(fill="x", padx=20, pady=10)

        # Repository selection controls
        controls_frame = ctk.CTkFrame(
            repo_frame,
            fg_color="transparent",
        )
        controls_frame.pack(fill="x", padx=20, pady=20)

        repo_label = ctk.CTkLabel(
            controls_frame,
            text="Select Repository:",
            text_color=self.colors['text'],
            font=("Inter", 12),
        )
        repo_label.pack(side="left", padx=(0, 10))

        self.repo_selection = ctk.StringVar()
        self.repo_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            variable=self.repo_selection,
            # Main button appearance
            fg_color=self.colors['background'],  # Background of the main button
            button_color=self.colors['primary'],  # Border/accent color
            button_hover_color=self.colors['primary_hover'],
            text_color=self.colors['text'],  # Text color for selected item

            # Dropdown menu appearance
            dropdown_fg_color=self.colors['surface'],  # Background of dropdown menu
            dropdown_hover_color=self.colors['primary_hover'],
            dropdown_text_color=self.colors['text'],  # Text color in dropdown list

            # Sizing and shape
            width=400,
            height=36,
            corner_radius=8,

            # Text styling
            font=("Inter", 12),

            # Ensure dropdown opens with enough space
            dropdown_font=("Inter", 12)
        )
        self.repo_dropdown.pack(side="left", padx=10)

        self.import_button = ctk.CTkButton(
            controls_frame,
            text="Import Milestones",
            command=self.import_milestones,
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_hover'],
            text_color=self.colors['text'],
            font=("Inter", 12, "bold"),
            height=36,
            corner_radius=8
        )
        self.import_button.pack(side="right")
        self.import_button.configure(state="disabled")

    def create_log_section(self):
        """Creates the logging section with modern styling"""
        log_container = ctk.CTkFrame(
            self.main_container,
            fg_color=self.colors['surface'],
            corner_radius=15,
        )
        log_container.pack(fill="both", expand=True, padx=20, pady=10)

        log_header = ctk.CTkLabel(
            log_container,
            text="Activity Log",
            text_color=self.colors['text'],
            font=("Inter", 14, "bold"),
        )
        log_header.pack(anchor="w", padx=20, pady=10)

        # Custom styled text widget for logs
        self.log_text = scrolledtext.ScrolledText(
            log_container,
            wrap="word",
            bg=self.colors['background'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            font=("Inter", 11),
            borderwidth=0,
            highlightthickness=1,
            highlightcolor=self.colors['border'],
            relief="flat"
        )
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def create_status_bar(self):
        """Creates the status bar with modern styling"""
        self.status_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=self.colors['surface'],
            corner_radius=15,
            height=50
        )
        self.status_frame.pack(fill="x", padx=20, pady=(10, 20))

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            text_color=self.colors['text_secondary'],
            font=("Inter", 12),
        )
        self.status_label.pack(side="left", padx=20, pady=10)

    def log_handler(self, record):
        """
        Handles incoming log messages and displays them in the log text area.
        Each log type (INFO, ERROR, etc.) is displayed with appropriate styling.
        """
        self.log_text.configure(state='normal')

        # Format timestamp for better readability
        timestamp = record.created.strftime("%H:%M:%S")

        # Define color coding for different log levels
        level_colors = {
            'INFO': '#10B981',  # Green for regular info
            'ERROR': '#EF4444',  # Red for errors
            'WARNING': '#F59E0B'  # Amber for warnings
        }

        # Get the color for this log level, default to text color if not found
        log_color = level_colors.get(record.levelname, self.colors['text'])

        # Insert the log message with timestamp and proper formatting
        self.log_text.insert('end', f"{timestamp} ", ('timestamp',))
        self.log_text.insert('end', f"{record.levelname}: ", ('level',))
        self.log_text.insert('end', f"{record.msg}\n", ('message',))

        # Apply color tags
        self.log_text.tag_config('timestamp', foreground=self.colors['text_secondary'])
        self.log_text.tag_config('level', foreground=log_color)
        self.log_text.tag_config('message', foreground=self.colors['text'])

        # Autoscroll to the latest message
        self.log_text.see('end')
        self.log_text.configure(state='disabled')

    def update_repo_dropdown(self):
        """
        Fetches and updates the repository dropdown with available GitHub repositories.
        Ensures proper text formatting and visibility.
        """
        if self.github_client:
            try:
                # Show loading state
                self.status_label.configure(text="Fetching repositories...")
                self.repo_dropdown.configure(state="disabled")

                # Get repositories from GitHub
                repos = self.github_client.get_user_repos()

                # Format repository names for better readability
                repo_list = []
                for repo in repos:
                    owner = repo['owner']['login']
                    name = repo['name']
                    # Add padding and formatting for better visibility
                    formatted_name = f"{owner}/{name}"
                    repo_list.append(formatted_name)

                # Update dropdown with improved styling
                self.repo_dropdown.configure(
                    values=repo_list,
                    state="normal",
                    # Refresh colors to ensure visibility
                    dropdown_fg_color=self.colors['surface'],
                    dropdown_text_color=self.colors['text'],
                    text_color=self.colors['text']
                )

                # If there are repositories, select the first one by default
                if repo_list:
                    self.repo_selection.set(repo_list[0])

                # Update status with success message
                self.status_label.configure(
                    text=f"Found {len(repo_list)} repositories",
                    text_color=self.colors['success']
                )

                self.logger.info(f"Successfully loaded {len(repo_list)} repositories")

            except Exception as e:
                # Handle errors gracefully
                error_message = f"Failed to fetch repositories: {str(e)}"
                self.status_label.configure(
                    text=error_message,
                    text_color=self.colors['error']
                )
                self.logger.error(error_message)
                self.repo_dropdown.configure(state="normal")

    def _enable_import_button(self, *args):
        """
        Controls the state of the import button based on repository selection.
        Provides visual feedback about the button's state.
        """
        if self.repo_selection.get():
            self.import_button.configure(
                state="normal",
                fg_color=self.colors['primary'],
                hover_color=self.colors['primary_hover']
            )
            # Update status to show readiness
            self.status_label.configure(
                text="Ready to import milestones",
                text_color=self.colors['text_secondary']
            )
        else:
            self.import_button.configure(
                state="disabled",
                fg_color=self.colors['surface'],
                hover_color=self.colors['surface']
            )
            # Update status to prompt for selection
            self.status_label.configure(
                text="Please select a repository",
                text_color=self.colors['text_secondary']
            )

    def import_milestones(self):
        """
        Handles the milestone import process with proper error handling and user feedback.
        Updates the UI to reflect the current state of the import process.
        """
        selected_repo = self.repo_selection.get()
        if not selected_repo:
            self.logger.error("No repository selected")
            return

        # Update UI to show import in progress
        self.import_button.configure(
            state="disabled",
            text="Importing...",
            fg_color=self.colors['surface']
        )
        self.status_label.configure(
            text=f"Importing milestones for {selected_repo}...",
            text_color=self.colors['text_secondary']
        )

        try:
            # Perform the import
            self.import_gui.run(selected_repo)

            # Update UI to show success
            self.status_label.configure(
                text="Import completed successfully!",
                text_color=self.colors['success']
            )
            self.logger.info(f"Successfully imported milestones for {selected_repo}")

        except Exception as e:
            # Handle import errors
            error_message = f"Import failed: {str(e)}"
            self.status_label.configure(
                text=error_message,
                text_color=self.colors['error']
            )
            self.logger.error(error_message)

        finally:
            # Reset button state
            self.import_button.configure(
                state="normal",
                text="Import Milestones",
                fg_color=self.colors['primary']
            )

    def on_close(self):
        """
        Handles the application closing process with a confirmation dialog.
        Ensures proper cleanup before closing.
        """
        if messagebox.askokcancel(
                "Quit",
                "Are you sure you want to quit?",
                icon='warning'
        ):
            # Perform any necessary cleanup
            self.logger.info("Application closing")
            self.root.destroy()

    def run(self):
        """
        Starts the main application loop.
        Sets up any final configurations before running.
        """
        # Center the window on the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 900
        window_height = 650

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Start the main event loop
        self.root.mainloop()