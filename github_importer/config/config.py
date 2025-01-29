# github_importer/config/config.py
import os
from dotenv import load_dotenv
from typing import List, Optional

load_dotenv()


class Config:
    def __init__(self):
        self.client_id: Optional[str] = os.getenv("GITHUB_CLIENT_ID")
        self.redirect_uri: Optional[str] = os.getenv("GITHUB_REDIRECT_URI")
        self.scope: List[str] = os.getenv(
            "GITHUB_SCOPE",
            "repo,repo:status,write:repo,write:issues"
        ).split(",")

    def __repr__(self) -> str:
        # Safely handle None values
        client_id_display = f"'{self.client_id[:5]}...'" if self.client_id else 'None'
        redirect_uri_display = f"'{self.redirect_uri}'" if self.redirect_uri else 'None'
        scope_display = f"'{','.join(self.scope)}'" if self.scope else '[]'

        return (f"Config(client_id={client_id_display}, "
                f"redirect_uri={redirect_uri_display}, "
                f"scope={scope_display})")

    def validate(self) -> bool:
        """Validate that required configuration is present"""
        return bool(self.client_id and self.redirect_uri and self.scope)

    def get_scope_string(self) -> str:
        """Get scope as a comma-separated string"""
        return ','.join(self.scope)

    @property
    def is_configured(self) -> bool:
        """Check if the configuration is complete"""
        return self.validate()