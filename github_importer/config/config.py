import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class to load settings from environment variables."""

    def __init__(self):
        self.client_id = os.getenv("GITHUB_CLIENT_ID")
        self.client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/callback")
        self.scope = os.getenv("GITHUB_SCOPE", "repo")

        if not all([self.client_id, self.client_secret]):
            raise ValueError("GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET must be set as environment variables.")

    def __repr__(self):
      return f"Config(client_id='{self.client_id[:5]}...', redirect_uri='{self.redirect_uri}', scope='{self.scope}')"