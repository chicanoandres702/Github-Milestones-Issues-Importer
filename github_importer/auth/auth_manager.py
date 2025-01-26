import webbrowser
import requests
from flask import Flask, request
import os


class AuthManager:
    def __init__(self, config, logger):
        self.client_id = config.client_id
        self.redirect_uri = config.redirect_uri
        self.scope = config.scope
        self.logger = logger
        self.on_auth_success = None

        self.app = Flask(__name__)
        self.app.add_url_rule('/callback', view_func=self.callback)
        self.server_port = 8000

    def get_authorization_url(self):
      scope = "%20".join(self.scope)
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

        # Exchange the code for an access token
        access_token = self.exchange_code_for_token(code)
        if access_token:
            # Call the success callback, passing in the access token
            if self.on_auth_success:
                self.on_auth_success(access_token)

            return "Authorization was successful! You can close this page.", 200

        else:
            return "Authorization failed.", 400

    def exchange_code_for_token(self, code):
        """Exchanges the authorization code for an access token."""
        url = "https://github.com/login/oauth/access_token"
        data = {
            "client_id": self.client_id,
            "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),  # Get from the env
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
          return json_response["access_token"]
        else:
           self.logger.error(f"An error has occurred: {json_response}")
           return None

    def set_on_auth_success(self, callback):
         """Sets the callback function to be executed upon successful authentication."""
         self.on_auth_success = callback