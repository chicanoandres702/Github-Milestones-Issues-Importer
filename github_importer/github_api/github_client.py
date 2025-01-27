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

    def _log_request(self, method, url, headers, data=None):
        self.logger.info(f"Request: {method} {url} Headers: {headers} Data: {data}")

    def _make_request(self, method, url, headers, data=None):
        try:
            if method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, json=data)
            elif method == "GET":
                response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return None

    def _handle_rate_limit(self, response):
        if response.status_code == 403 and "X-RateLimit-Remaining" in response.headers and response.headers["X-RateLimit-Remaining"] == "0":
            self.logger.warning("Rate limit exceeded. Waiting for reset.")
            reset_time = int(response.headers["X-RateLimit-Reset"])
            sleep_time = max(0, reset_time - time.time())
            time.sleep(sleep_time)
            return True
        return False

    def _sleep(self):
        time.sleep(1)

    def create_temporary_milestone(self, repo_owner, repo_name):
        """Creates a temporary milestone to associate issues if none can be found"""
        milestone_data = {
            "title": "Temporary Milestone For Import",
            "state": "open",
            "description": "This milestone is used as a container to import issues from the json file"
        }
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/milestones"
        self._log_request("POST", url, self.headers, milestone_data)
        response = self._make_request("POST", url, self.headers, milestone_data)

        if response:
            if self._handle_rate_limit(response):
                response = self._make_request("POST", url, self.headers, milestone_data)
            self.logger.info(f"Successfully created temporary milestone")
            return response.json()
        else:
            return None


    def get_user_info(self):
        """Retrieves the authenticated user's information."""
        url = f"{self.base_url}/user"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            self.logger.info(f"Successfully retrieved User info: {data}")
            return data
        except Exception as e:
            self.logger.error(f"An error has occurred getting user info: {e}")
            return None

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

    def create_milestone(self, repo_owner, repo_name, milestone_data):
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/milestones"
        self._log_request("POST", url, self.headers, milestone_data)
        response = self._make_request("POST", url, self.headers, milestone_data)

        if response:
            if self._handle_rate_limit(response):
                response = self._make_request("POST", url, self.headers, milestone_data)

            if response.status_code == 201:
                self.logger.info(f"Successfully created milestone: {milestone_data['title']}")
                return response.json()
            else:
                self.logger.error(f"Failed to create milestone: {response.status_code} - {response.text}")
                return None
        else:
            self.logger.error("No response received from the GitHub API.")
            return None

    def create_issue(self, repo_owner, repo_name, issue_data):
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
        self._log_request("POST", url, self.headers, issue_data)
        response = self._make_request("POST", url, self.headers, issue_data)
        if response:
            if self._handle_rate_limit(response):
                response = self._make_request("POST", url, self.headers, issue_data)
            self._sleep()
            self.logger.info(f"Successfully created issue: {issue_data['title']}")
            return response.json()
        else:
            return None

    def delete_issue(self, repo_owner, repo_name, issue_number):
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}"
        self._log_request("DELETE", url, self.headers)
        response = self._make_request("DELETE", url, self.headers)
        if response:
            if self._handle_rate_limit(response):
                response = self._make_request("DELETE", url, self.headers)
            if response.status_code == 404:
                self.logger.warning(f"Issue with id {issue_number} not found.")
            else:
                self.logger.info(f"Successfully deleted issue with id: {issue_number}")
            return response.status_code
        else:
            return None

    def delete_milestone(self, repo_owner, repo_name, milestone_number):
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/milestones/{milestone_number}"
        self._log_request("DELETE", url, self.headers)
        response = self._make_request("DELETE", url, self.headers)
        if response:
            if self._handle_rate_limit(response):
                response = self._make_request("DELETE", url, self.headers)
            self.logger.info(f"Successfully deleted milestone: {milestone_number}")
            return response.status_code
        else:
            return None

    def get_issues(self, repo_owner, repo_name):
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
        self._log_request("GET", url, self.headers)
        response = self._make_request("GET", url, self.headers)
        if response:
            if self._handle_rate_limit(response):
                response = self._make_request("GET", url, self.headers)
            return response.json()
        else:
            return None

    def create_temporary_milestone(self, repo_owner, repo_name):
        """Creates a temporary milestone to associate issues if none can be found"""
        milestone_data = {
            "title": "Temporary Milestone For Import",
            "state": "open",
            "description": "This milestone is used as a container to import issues from the json file"
        }
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/milestones"
        self._log_request("POST", url, self.headers, milestone_data)
        response = self._make_request("POST", url, self.headers, milestone_data)

        if response:
            if self._handle_rate_limit(response):
                response = self._make_request("POST", url, self.headers, milestone_data)
            self.logger.info(f"Successfully created temporary milestone")
            return response.json()
        else:
            return None

    def delete_all_issues(self, repo_owner, repo_name):
        """
        Deletes all issues in the specified repository using the GitHub GraphQL API.
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # GraphQL query to get all issues
        query = """
        query($repoOwner: String!, $repoName: String!) {
            repository(owner: $repoOwner, name: $repoName) {
                issues(last: 100) {
                    nodes {
                        id
                        number
                    }
                }
            }
        }
        """

        # GraphQL mutation to delete an issue
        mutation = """
        mutation($issueId: ID!) {
            deleteIssue(input: {issueId: $issueId}) {
                clientMutationId
            }
        }
        """

        # Function to execute a GraphQL query
        def graphql_query(query, variables):
            response = requests.post(
                'https://api.github.com/graphql',
                json={'query': query, 'variables': variables},
                headers=headers
            )
            response.raise_for_status()
            return response.json()

        # Get all issues
        variables = {"repoOwner": repo_owner, "repoName": repo_name}
        result = graphql_query(query, variables)
        issues = result['data']['repository']['issues']['nodes']

        # Delete each issue
        for issue in issues:
            issue_id = issue['id']
            self.logger.info(f"Deleting issue: {issue_id}")
            variables = {"issueId": issue_id}
            try:
                graphql_query(mutation, variables)
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Failed to delete issue {issue_id}: {e}")