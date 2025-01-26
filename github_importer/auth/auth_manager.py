import requests
import webbrowser
import json
from flask import Flask, request
from threading import Thread


class AuthManager:
    """Manages GitHub authentication."""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.access_token = None
        self.server = None

    def authorize_github(self):
        """Opens the browser for GitHub authorization."""
        url = f"https://github.com/login/oauth/authorize?client_id={self.config.client_id}&redirect_uri={self.config.redirect_uri}&scope={self.config.scope}"
        webbrowser.open_new_tab(url)
        self._start_local_server()

    def _start_local_server(self):
        """Starts a local server to handle OAuth redirect."""
        app = Flask(__name__)
        self.server = app

        @app.route("/callback")
        def callback():
            code = request.args.get("code")
            self.access_token = self._get_access_token(code)
            return "Authentication successful! You can close this page.", 200

        thread = Thread(target=app.run, kwargs={"port": 8000})
        thread.daemon = True  # close the server when main thread exits
        thread.start()

    def _get_access_token(self, code):
        """Exchanges the code for an access token."""
        url = "https://github.com/login/oauth/access_token"
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code
        }
        headers = {"Accept": "application/json"}
        try:
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data["access_token"]
            self.logger.info("Successfully retrieved access token")
            self.server.shutdown()
            return access_token
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting access token: {e}")
            return None

    def get_access_token(self):
        return self.access_token