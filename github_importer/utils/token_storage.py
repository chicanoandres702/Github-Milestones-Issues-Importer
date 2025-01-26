import json
import os

class TokenStorage:
    def __init__(self, file_path="tokens.json"):
        self.file_path = file_path

    def save_tokens(self, access_token, refresh_token):
        """Saves the access and refresh tokens to a JSON file."""
        try:
            tokens = {
                "access_token": access_token,
                "refresh_token": refresh_token
             }
            with open(self.file_path, 'w') as f:
                json.dump(tokens, f)
        except Exception as e:
            raise Exception(f"Error writing token file: {e}")

    def load_tokens(self):
        """Loads the access and refresh tokens from a JSON file."""
        try:
            if not os.path.exists(self.file_path):
               return None, None
            with open(self.file_path, 'r') as f:
                tokens = json.load(f)
                return tokens.get("access_token"), tokens.get("refresh_token")

        except Exception as e:
            raise Exception(f"Error reading token file: {e}")