# github_importer/github_api/github_client.py
import requests
from github_importer.utils.logger import Logger

class GitHubClient:
    def __init__(self, access_token, logger, auth_manager):
        self.access_token = access_token
        self.logger = logger
        self.auth_manager = auth_manager
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.access_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def authenticate(self):
        """Authenticates with the GitHub API using the stored access token."""
        url = f"{self.base_url}/user"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            self.logger.info("Successfully authenticated with GitHub API.")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to authenticate with GitHub API: {e}")
            # If authentication fails due to invalid token, try refreshing
            if response.status_code == 401:
                self.logger.info("Access token is invalid, trying to refresh.")
                if self.auth_manager.refresh_access_token():
                    self.headers["Authorization"] = f"token {self.auth_manager.access_token}"
                    self.logger.info("Token refreshed successfully.")
                    return True  # Try authenticating again after refresh
                else:
                    self.logger.error("Failed to refresh access token.")
            return False

    def check_access_token(self):
        url = f"{self.base_url}/user"
        try:
            response = requests.get(url, headers=self.headers)
            return response.status_code
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to check access token: {e}")
            return None

    def get_user_repos(self):
        """Fetches the authenticated user's repositories."""
        try:
            response = requests.get(f"{self.base_url}/user/repos", headers=self.headers)
            response.raise_for_status()
            repos = response.json()
            self.logger.info(f"Successfully fetched user repositories: {repos}")
            return repos
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch user repositories: {e}")
            return None

    def get_repo_contents(self, repo_name, path=""):
        """Fetches the contents of a repository at the specified path."""
        try:
            url = f"{self.base_url}/repos/{repo_name}/contents/{path}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            contents = response.json()
            self.logger.info(f"Successfully fetched repository contents for {repo_name}/{path}: {contents}")
            return contents
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch repository contents for {repo_name}/{path}: {e}")
            return None

    def create_repo(self, repo_name, description=""):
        """Creates a new repository for the authenticated user."""
        try:
            url = f"{self.base_url}/user/repos"
            data = {
                "name": repo_name,
                "description": description,
                "private": False  # You can change this to True for private repos
            }
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            repo = response.json()
            self.logger.info(f"Successfully created repository: {repo}")
            return repo
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to create repository: {e}")
            return None

    def create_file(self, repo_name, path, content, message="Add file"):
        """Creates a new file in the specified repository."""
        try:
            url = f"{self.base_url}/repos/{repo_name}/contents/{path}"
            data = {
                "message": message,
                "content": content
            }
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            file_info = response.json()
            self.logger.info(f"Successfully created file {path} in {repo_name}: {file_info}")
            return file_info
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to create file {path} in {repo_name}: {e}")
            return None

    def update_file(self, repo_name, path, content, sha, message="Update file"):
        """Updates an existing file in the specified repository."""
        try:
            url = f"{self.base_url}/repos/{repo_name}/contents/{path}"
            data = {
                "message": message,
                "content": content,
                "sha": sha
            }
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            file_info = response.json()
            self.logger.info(f"Successfully updated file {path} in {repo_name}: {file_info}")
            return file_info
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to update file {path} in {repo_name}: {e}")
            return None

    def delete_file(self, repo_name, path, sha, message="Delete file"):
        """Deletes a file from the specified repository."""
        try:
            url = f"{self.base_url}/repos/{repo_name}/contents/{path}"
            data = {
                "message": message,
                "sha": sha
            }
            response = requests.delete(url, headers=self.headers, json=data)
            response.raise_for_status()
            self.logger.info(f"Successfully deleted file {path} from {repo_name}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to delete file {path} from {repo_name}: {e}")