import requests
import webbrowser
import json
from flask import Flask, request
from threading import Thread
import traceback  # Import traceback for detailed error info


class AuthManager:
    """Manages GitHub authentication."""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.access_token = None
        self.server = None
        self.token_retrieved = False  # Flag to ensure _get_access_token is called only once
        self.on_auth_success = None

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
            try:
                if self.token_retrieved:  # Ensure _get_access_token is only called once
                    self.logger.warning(
                        "Callback was triggered multiple times. Access token has already been retrieved.")
                    return "Authentication successful! You can close this page. (Token already retrieved)", 200
                code = request.args.get("code")
                self.logger.info(f"Received authorization code: {code}")
                access_token = self._get_access_token(code, request)  # pass in the request to _get_access_token
                if access_token:
                    self.access_token = access_token
                    self.token_retrieved = True
                    if self.on_auth_success:
                        self.on_auth_success(access_token)  # Call the success callback with the token
                    return "Authentication successful! You can close this page.", 200
                else:
                    return "Authentication Failed (See logs for more info)", 400
            except Exception as e:
                self.logger.error(f"An unexpected error in callback function occurred: {e} - {traceback.format_exc()}")
                return "Authentication Failed: an unexpected error occurred (See logs for more info)", 500

        thread = Thread(target=app.run, kwargs={"port": 8000})
        thread.daemon = True
        thread.start()

    def _get_access_token(self, code, request):
        """Exchanges the code for an access token."""
        url = "https://github.com/login/oauth/access_token"
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code
        }
        headers = {"Accept": "application/json"}
        try:
            self.logger.info(f"Making POST request to {url}")
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data.get("access_token")
            if not access_token:
                self.logger.error(f"Access token not found in response: {token_data}")
                return None
            self.logger.info("Successfully retrieved access token")
            # Correct way to shut down Flask development server
            shutdown_server = request.environ.get('werkzeug.server.shutdown')
            if shutdown_server:
                shutdown_server()
            return access_token
        except requests.exceptions.RequestException as e:
            self.logger.error(
                f"Error getting access token: {e} - {response.status_code} - {response.text} - {traceback.format_exc()}")
            return None
        except Exception as e:
            self.logger.error(f"An unexpected error in _get_access_token occurred: {e} - {traceback.format_exc()}")
            return None

    def set_on_auth_success(self, callback):
        self.on_auth_success = callback

    def get_access_token(self):
        return self.access_token