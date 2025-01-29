# github_importer/auth/auth_manager.py
import webbrowser
import requests
from flask import Flask, request
import os
import json
from github_importer.utils.token_storage import TokenStorage


class AuthManager:
    def __init__(self, config, logger):
        self.client_id = config.client_id
        self.redirect_uri = config.redirect_uri
        self.scope = config.scope
        self.logger = logger
        self.on_auth_success = None
        self.access_token = None
        self.refresh_token = None
        self.token_storage = TokenStorage()
        self.load_stored_tokens()

        self.app = Flask(__name__)
        self.app.add_url_rule('/callback', view_func=self.callback)
        self.server_port = 8000

    def load_stored_tokens(self):
        try:
            access_token, refresh_token = self.token_storage.load_tokens()
            if access_token and refresh_token:
                self.logger.info("Successfully loaded stored access and refresh tokens.")
                self.access_token = access_token
                self.refresh_token = refresh_token
                if self.on_auth_success:
                    self.on_auth_success(self.access_token)
            else:
                self.logger.info("No stored tokens found.")
        except Exception as e:
            self.logger.error(f"An error has occurred loading tokens: {e}")

    def get_authorization_url(self):
        scope = "%20".join(self.scope)
        self.logger.info(f"Requesting these scopes: {self.scope}")
        url = (f"https://github.com/login/oauth/authorize?"
               f"client_id={self.client_id}"
               f"&redirect_uri={self.redirect_uri}"
               f"&scope={scope}")
        return url

    def start_auth_server(self):
        """Starts the Flask server to handle the GitHub authorization callback."""
        self.app.run(port=self.server_port)

    def start_oauth_flow(self):
        """Starts the OAuth 2.0 flow by opening the authorization URL in the browser."""
        url = self.get_authorization_url()
        webbrowser.open(url)

        # Start the Flask app to handle the callback in a non-blocking way
        import threading
        auth_server_thread = threading.Thread(target=self.start_auth_server)
        auth_server_thread.daemon = True  # set the thread as daemon
        auth_server_thread.start()

    def callback(self):
        """Handles the callback from GitHub after authorization."""
        code = request.args.get('code')
        self.logger.info(f"Received authorization code: {code}")
        token_response = self.exchange_code_for_token(code)

        if token_response:
            self.access_token = token_response.get("access_token")
            self.refresh_token = token_response.get("refresh_token")
            try:
                self.token_storage.save_tokens(self.access_token, self.refresh_token)
            except Exception as e:
                self.logger.error(f"An error has occurred saving the tokens: {e}")

            # Execute the callback if it exists
            if self.on_auth_success:
                self.on_auth_success(self.access_token)

            return "Authorization was successful! You can close this page.", 200
        else:
            return "Authorization failed.", 400

    def exchange_code_for_token(self, code):
        """Exchanges the authorization code for an access token."""
        url = "https://github.com/login/oauth/access_token"
        data = {
            "client_id": self.client_id,
            "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
            "code": code,
            "redirect_uri": self.redirect_uri
        }

        self.logger.info("Making POST request to https://github.com/login/oauth/access_token")

        headers = {'Accept': 'application/json'}
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        json_response = response.json()
        if "access_token" in json_response:
            self.logger.info("Successfully retrieved access token")
            return json_response
        else:
            self.logger.error(f"An error has occurred: {json_response}")
            return None

    def set_on_auth_success(self, callback):
        """Sets the callback function to be executed upon successful authentication."""
        # Store the callback without executing it
        self.on_auth_success = callback

        # If we already have a token, execute the callback
        if self.access_token:
            self.logger.info("Executing callback with existing token")
            callback(self.access_token)

    def refresh_access_token(self):
        """Exchanges the refresh token for a new access token."""
        if not self.refresh_token:
            self.logger.error("No refresh token available to use to retrieve access token.")
            return False

        url = "https://github.com/login/oauth/access_token"
        data = {
            "client_id": self.client_id,
            "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        self.logger.info("Making POST request to refresh access token")
        headers = {'Accept': 'application/json'}
        response = requests.post(url, json=data, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error refreshing access token: {e}")
            return False

        json_response = response.json()

        if "access_token" in json_response:
            self.logger.info("Successfully refreshed access token.")
            self.access_token = json_response["access_token"]
            self.refresh_token = json_response.get("refresh_token", self.refresh_token)

            # Save the new tokens
            try:
                self.token_storage.save_tokens(self.access_token, self.refresh_token)
            except Exception as e:
                self.logger.error(f"Error saving refreshed tokens: {e}")

            return True
        else:
            self.logger.error(f"Error when refreshing access token: {json_response}")
            return False