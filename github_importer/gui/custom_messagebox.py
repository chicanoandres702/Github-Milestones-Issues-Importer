# github_importer/gui/custom_messagebox.py

import customtkinter as ctk


class CustomMessageBox(ctk.CTkToplevel):
    def __init__(
            self,
            master,
            title="",
            message="",
            option_1="Cancel",
            option_2="OK",
            button_color=None,
            button_hover_color=None,
            cancel_button_color=None
    ):
        super().__init__(master)
        self.title(title)

        # Configure appearance
        self.configure(fg_color="#161B22")  # Dark GitHub background

        # Make modal
        self.transient(master)
        self.grab_set()

        # Center the message box
        window_width = 500  # Wider window
        window_height = 250  # Taller window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.result = None

        # Create main frame
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="#161B22",  # Match window background
            corner_radius=10
        )
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Message label
        self.message_label = ctk.CTkLabel(
            self.main_frame,
            text=message,
            wraplength=450,  # Increased wraplength
            font=("Segoe UI", 16),  # Larger, more readable font
            text_color="#C9D1D9",  # GitHub light text color
            justify="center"
        )
        self.message_label.pack(pady=(30, 40), padx=20)

        # Button frame
        self.button_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.button_frame.pack(fill="x", pady=(0, 20), padx=20)

        # Button container to ensure proper spacing
        button_container = ctk.CTkFrame(
            self.button_frame,
            fg_color="transparent"
        )
        button_container.pack(expand=True, fill="x")

        # Cancel button
        self.cancel_button = ctk.CTkButton(
            button_container,
            text=option_1,
            fg_color=cancel_button_color or "#30363D",  # GitHub secondary color
            hover_color="#40464E",
            text_color="#C9D1D9",
            height=50,  # Taller button
            width=200,  # Fixed width
            font=("Segoe UI", 16, "bold"),
            corner_radius=8,
            command=self._on_cancel
        )
        self.cancel_button.pack(side="left", padx=(0, 10))

        # OK button
        self.ok_button = ctk.CTkButton(
            button_container,
            text=option_2,
            fg_color=button_color or "#2EA043",  # GitHub primary green
            hover_color="#3FB950",
            text_color="white",
            height=50,  # Taller button
            width=200,  # Fixed width
            font=("Segoe UI", 16, "bold"),
            corner_radius=8,
            command=self._on_ok
        )
        self.ok_button.pack(side="right")

        # Make dialog modal
        self.wait_window()

    def _on_cancel(self):
        self.result = "Cancel"
        self.destroy()

    def _on_ok(self):
        self.result = "OK"
        self.destroy()

    def get(self):
        return self.result