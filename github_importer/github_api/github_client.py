import requests
from typing import List, Dict, Any, Optional, Callable
import time
import logging
import threading
from queue import Queue


class GitHubClient:
    """
    Comprehensive GitHub API client supporting both REST and GraphQL interactions.

    Attributes:
        token (str): GitHub API authentication token
        logger (logging.Logger): Logger for tracking API interactions
        base_url (str): Base URL for GitHub REST API
        graphql_url (str): URL for GitHub GraphQL API
    """

    def __init__(self, token: str, logger: logging.Logger, auth_manager: Any):
        """
        Initialize the GitHub client.

        Args:
            token: GitHub API token
            logger: Logger instance
            auth_manager: Authentication manager
        """
        self.token = token
        self.logger = logger
        self.auth_manager = auth_manager
        self.base_url = "https://api.github.com"
        self.graphql_url = "https://api.github.com/graphql"
        self.headers = self._get_headers()
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

    def _sleep(self):
        time.sleep(2)

    def _get_headers(self) -> Dict[str, str]:
        """
        Generate headers for API requests.

        Returns:
            Dict of headers including authorization
        """
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def _graphql_headers(self) -> Dict[str, str]:
        """
        Generate headers for GraphQL requests.

        Returns:
            Dict of headers including authorization and content type
        """
        return {
            "Authorization": f"bearer {self.token}",
            "Content-Type": "application/json"
        }

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """
        Update and handle GitHub API rate limits.

        Args:
            response: API response
        """
        self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        self.rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))

        if self.rate_limit_remaining < 10:
            wait_time = max(self.rate_limit_reset - time.time(), 0)
            self.logger.warning(f"Rate limit low. Waiting {wait_time} seconds.")
            time.sleep(wait_time)

    def _log_request(self, method, url, headers, data=None):
        self.logger.info(f"Request: {method} {url} Headers: {headers} Data: {data}")

    def _make_request(self, method: str, url: str, params: Dict = None, json: Dict = None,
                      **kwargs) -> requests.Response:
        """
        Make a generic API request with error handling.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters for the request
            json: JSON body for the request
            **kwargs: Additional request parameters

        Returns:
            API response
        """
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=json,
                **kwargs
            )
            self._handle_rate_limit(response)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API Request Error: {e}")
            raise

    def delete_milestone(self, repo_owner, repo_name, milestone_number):
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/milestones/{milestone_number}"
        self._log_request("DELETE", url, self.headers)
        response = self._make_request("DELETE", url, self.headers)
        if response:
            self.logger.info(f"Successfully deleted milestone: {milestone_number}")
            return response.status_code
        else:
            return None

    def create_issue(self, repo_owner, repo_name, issue_data):
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
        self._log_request("POST", url, self.headers, issue_data)
        response = self._make_request("POST", url, self.headers, issue_data)
        if response:
            if response.status_code == 201:
                self.logger.info(f"Successfully created issue: {issue_data['title']}")
                return response.json()
            else:
                self.logger.error(f"Failed to create issue: {response.status_code} - {response.text}")
                return None
        else:
            self.logger.error("No response received from the GitHub API.")
            return None



    def create_milestone(self, repo_owner, repo_name, milestone_data):
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/milestones"
        self._log_request("POST", url, self.headers, milestone_data)
        response = self._make_request("POST", url, self.headers, milestone_data)
        if response:
            if response.status_code == 201:
                self.logger.info(f"Successfully created milestone: {milestone_data['title']}")
                return response.json()
            else:
                self.logger.error(f"Failed to create milestone: {response.status_code} - {response.text}")
                return None
        else:
            self.logger.error("No response received from the GitHub API.")
            return None


    def get_user_repos(self) -> List[Dict[str, Any]]:
        """
        Retrieve user's repositories.

        Returns:
            List of repository dictionaries
        """
        url = f"{self.base_url}/user/repos"
        response = self._make_request('GET', url, params={'per_page': 100})
        return response.json()

    def get_milestones_with_issues(self, repo_owner: str, repo_name: str, state: str = "all") -> List[Dict[str, Any]]:
        """
        Get milestones with their associated issues.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            state: Milestone state filter (all, open, closed)

        Returns:
            List of milestones with nested issues
        """
        try:
            # First, get all milestones
            milestones_url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/milestones"
            milestones_params = {
                "state": state,
                "per_page": 100
            }
            milestones = []

            # Fetch milestones with pagination
            while milestones_url:
                milestones_response = self._make_request('GET', milestones_url, params=milestones_params)
                milestones.extend(milestones_response.json())

                # Check for pagination
                if 'next' in milestones_response.links:
                    milestones_url = milestones_response.links['next']['url']
                    milestones_params = {}  # Clear params for subsequent pages
                else:
                    milestones_url = None

            # For each milestone, fetch its issues
            for milestone in milestones:
                milestone_number = milestone['number']
                issues_url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/issues"
                issues_params = {
                    "milestone": milestone_number,
                    "state": "all",
                    "per_page": 100
                }

                milestone_issues = []
                current_issues_url = issues_url

                while current_issues_url:
                    issues_response = self._make_request('GET', current_issues_url, params=issues_params)
                    issues_data = issues_response.json()

                    for issue in issues_data:
                        formatted_issue = {
                            "title": issue['title'],
                            "number": issue['number'],
                            "state": issue['state'],
                            "body": issue['body'] or "",
                            "created_at": issue['created_at'],
                            "updated_at": issue['updated_at'],
                            "labels": [label['name'] for label in issue['labels']],
                            "comments_count": issue['comments']
                        }

                        if issue['comments'] > 0:
                            comments_url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/issues/{issue['number']}/comments"
                            comments_response = self._make_request('GET', comments_url)
                            formatted_issue['comments'] = [
                                {
                                    'body': comment['body'],
                                    'created_at': comment['created_at'],
                                    'author': comment['user']['login']
                                }
                                for comment in comments_response.json()
                            ]

                        milestone_issues.append(formatted_issue)

                    if 'next' in issues_response.links:
                        current_issues_url = issues_response.links['next']['url']
                        issues_params = {}
                    else:
                        current_issues_url = None

                milestone['issues'] = milestone_issues

            self.logger.info(f"Retrieved {len(milestones)} milestones with their issues")
            return milestones

        except Exception as e:
            error_msg = f"Failed to retrieve milestones with issues: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def delete_all_issues(self, repo_owner: str, repo_name: str, status_callback: Optional[Callable] = None) -> threading.Thread:
        """
        Delete all issues in a repository using GraphQL on a separate thread.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            status_callback: Callback function to update UI status

        Returns:
            Thread object handling the deletion process
        """
        def deletion_worker():
            try:
                # First, get all issue node IDs
                query = """
                query GetRepositoryIssues($owner: String!, $repo: String!) {
                    repository(owner: $owner, name: $repo) {
                        issues(first: 100, states: [OPEN, CLOSED]) {
                            nodes {
                                id
                                number
                                title
                            }
                            pageInfo {
                                hasNextPage
                                endCursor
                            }
                        }
                    }
                }
                """

                variables = {
                    "owner": repo_owner,
                    "repo": repo_name
                }

                # Collect all issue node IDs
                all_issues = []
                has_next_page = True
                cursor = None

                if status_callback:
                    status_callback("Fetching issues...")

                while has_next_page:
                    if cursor:
                        query = """
                        query GetRepositoryIssues($owner: String!, $repo: String!, $cursor: String!) {
                            repository(owner: $owner, name: $repo) {
                                issues(first: 100, states: [OPEN, CLOSED], after: $cursor) {
                                    nodes {
                                        id
                                        number
                                        title
                                    }
                                    pageInfo {
                                        hasNextPage
                                        endCursor
                                    }
                                }
                            }
                        }
                        """
                        variables["cursor"] = cursor

                    payload = {
                        "query": query,
                        "variables": variables
                    }

                    response = requests.post(
                        self.graphql_url,
                        headers=self._graphql_headers(),
                        json=payload
                    )
                    response.raise_for_status()
                    result = response.json()

                    if 'errors' in result:
                        raise Exception(f"GraphQL Error: {result['errors']}")

                    issues = result['data']['repository']['issues']
                    all_issues.extend(issues['nodes'])

                    has_next_page = issues['pageInfo']['hasNextPage']
                    cursor = issues['pageInfo']['endCursor']

                total_issues = len(all_issues)
                if status_callback:
                    status_callback(f"Found {total_issues} issues to delete")

                for index, issue in enumerate(all_issues, 1):
                    try:
                        if status_callback:
                            status_message = (
                                f"Deleting issue {index}/{total_issues}: "
                                f"#{issue['number']} - {issue['title']}"
                            )
                            status_callback(status_message)

                        self.delete_issue_graphql(issue['id'])
                        time.sleep(0.5)  # Rate limiting delay

                    except Exception as e:
                        error_msg = f"Error deleting issue #{issue['number']}: {str(e)}"
                        self.logger.error(error_msg)
                        if status_callback:
                            status_callback(error_msg)

                if status_callback:
                    status_callback(f"Successfully deleted {total_issues} issues")

            except Exception as e:
                error_msg = f"Failed to delete issues: {str(e)}"
                self.logger.error(error_msg)
                if status_callback:
                    status_callback(error_msg)
                raise Exception(error_msg)

        deletion_thread = threading.Thread(target=deletion_worker)
        deletion_thread.daemon = True
        deletion_thread.start()
        return deletion_thread

    def delete_issue_graphql(self, issue_node_id: str) -> Dict[str, Any]:
        """
        Delete an issue using GitHub GraphQL API.

        Args:
            issue_node_id: Node ID of the issue to delete

        Returns:
            GraphQL mutation response
        """
        query = """
        mutation DeleteIssue($input: DeleteIssueInput!) {
            deleteIssue(input: $input) {
                repository {
                    id
                }
            }
        }
        """

        variables = {
            "input": {
                "issueId": issue_node_id
            }
        }

        payload = {
            "query": query,
            "variables": variables
        }

        try:
            response = requests.post(
                self.graphql_url,
                headers=self._graphql_headers(),
                json=payload
            )
            response.raise_for_status()
            result = response.json()

            if 'errors' in result:
                raise Exception(f"GraphQL Error: {result['errors']}")

            return result

        except requests.exceptions.RequestException as e:
            self.logger.error(f"GraphQL Request Error: {e}")
            raise

    def authenticate(self) -> bool:
        """
        Verify authentication with GitHub API.

        Returns:
            bool: True if authentication is successful
        """
        try:
            url = f"{self.base_url}/user"
            response = self._make_request('GET', url)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False


# Example usage with status window
if __name__ == "__main__":
    import tkinter as tk
    from tkinter import ttk

    class StatusWindow:
        def __init__(self):
            self.root = tk.Tk()
            self.root.title("Issue Deletion Status")
            self.root.geometry("400x150")

            self.status_label = ttk.Label(self.root, text="", wraplength=380)
            self.status_label.pack(pady=20)

            self.progress = ttk.Progressbar(self.root, mode='indeterminate')
            self.progress.pack(fill=tk.X, padx=20)

        def update_status(self, message: str):
            self.status_label.config(text=message)
            self.root.update()

        def start_deletion(self, github_client, repo_owner: str, repo_name: str):
            self.progress.start()
            deletion_thread = github_client.delete_all_issues(
                repo_owner,
                repo_name,
                status_callback=self.update_status
            )

            def check_thread():
                if deletion_thread.is_alive():
                    self.root.after(100, check_thread)
                else:
                    self.progress.stop()
                    self.update_status("Deletion completed!")

            check_thread()

        def run(self):
            self.root.mainloop()

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Initialize GitHub client
    github_client = GitHubClient(
        token="your_github_token",
        logger=logger,
        auth_manager=None
    )

    # Create and run status window
    status_window = StatusWindow()
    status_window.start_deletion(
        github_client,
        repo_owner="example_owner",
        repo_name="example_repo"
    )
    status_window.run()