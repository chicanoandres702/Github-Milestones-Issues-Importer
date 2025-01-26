import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.client_id = os.getenv("GITHUB_CLIENT_ID")
        self.redirect_uri = os.getenv("GITHUB_REDIRECT_URI")
        self.scope = os.getenv("GITHUB_SCOPE", "repo,repo:status,write:repo,write:issues,offline_access").split(",")

    def __repr__(self):
        return f"Config(client_id='{self.client_id[:5]}...', redirect_uri='{self.redirect_uri}', scope='{','.join(self.scope)}')"