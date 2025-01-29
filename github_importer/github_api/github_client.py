# github_importer/github_api/github_client.py

import requests
from typing import List, Dict, Any, Optional
import time
import logging


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

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make a generic API request with error handling.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            API response
        """
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            self._handle_rate_limit(response)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API Request Error: {e}")
            raise

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

                # Prepare issues URL and parameters
                issues_url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/issues"
                issues_params = {
                    "milestone": milestone_number,
                    "state": "all",
                    "per_page": 100
                }

                milestone_issues = []
                current_issues_url = issues_url

                # Fetch issues for this milestone with pagination
                while current_issues_url:
                    issues_response = self._make_request('GET', current_issues_url, params=issues_params)
                    issues_data = issues_response.json()

                    # Process each issue
                    for issue in issues_data:
                        # Prepare issue details
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

                        # Fetch comments if they exist
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

                    # Check for pagination of issues
                    if 'next' in issues_response.links:
                        current_issues_url = issues_response.links['next']['url']
                        issues_params = {}  # Clear params for subsequent pages
                    else:
                        current_issues_url = None

                # Add issues to the milestone
                milestone['issues'] = milestone_issues

            self.logger.info(f"Retrieved {len(milestones)} milestones with their issues")
            return milestones

        except Exception as e:
            error_msg = f"Failed to retrieve milestones with issues: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)


    def create_milestone(self, repo_owner: str, repo_name: str, milestone_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new milestone in a repository.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            milestone_data: Milestone details

        Returns:
            Created milestone data
        """
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/milestones"
        response = self._make_request('POST', url, json=milestone_data)
        return response.json()

    def delete_milestone(self, repo_owner: str, repo_name: str, milestone_number: int) -> None:
        """
        Delete a milestone from a repository.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            milestone_number: Milestone number to delete
        """
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/milestones/{milestone_number}"
        self._make_request('DELETE', url)

    def create_issue(self, repo_owner: str, repo_name: str, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new issue in a repository.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            issue_data: Issue details

        Returns:
            Created issue data
        """
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/issues"
        response = self._make_request('POST', url, json=issue_data)
        return response.json()

    def delete_all_issues(self, repo_owner: str, repo_name: str) -> None:
        """
        Delete all issues in a repository using GraphQL.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
        """
        try:
            # First, get all issue node IDs
            query = """
            query GetRepositoryIssues($owner: String!, $repo: String!) {
                repository(owner: $owner, name: $repo) {
                    issues(first: 100, states: [OPEN, CLOSED]) {
                        nodes {
                            id
                            number
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
            all_issue_node_ids = []
            has_next_page = True
            cursor = None

            while has_next_page:
                # Update variables with cursor for pagination
                if cursor:
                    query = """
                    query GetRepositoryIssues($owner: String!, $repo: String!, $cursor: String!) {
                        repository(owner: $owner, name: $repo) {
                            issues(first: 100, states: [OPEN, CLOSED], after: $cursor) {
                                nodes {
                                    id
                                    number
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

                # Make GraphQL request
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

                # Check for GraphQL errors
                if 'errors' in result:
                    raise Exception(f"GraphQL Error: {result['errors']}")

                # Extract issue node IDs
                issues = result['data']['repository']['issues']
                all_issue_node_ids.extend([issue['id'] for issue in issues['nodes']])

                # Update pagination info
                has_next_page = issues['pageInfo']['hasNextPage']
                cursor = issues['pageInfo']['endCursor']

            # Delete issues individually
            self.delete_issues_individually(all_issue_node_ids)

            self.logger.info(f"Deleted {len(all_issue_node_ids)} issues in {repo_owner}/{repo_name}")

        except Exception as e:
            error_msg = f"Failed to delete issues: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def delete_issues_individually(self, issue_node_ids: List[str]) -> None:
        """
        Delete issues one by one using GraphQL mutations.

        Args:
            issue_node_ids: List of issue node IDs to delete
        """
        # GraphQL mutation for deleting a single issue
        mutation = """
        mutation DeleteIssue($input: DeleteIssueInput!) {
            deleteIssue(input: $input) {
                clientMutationId
            }
        }
        """

        # Delete issues one by one
        for node_id in issue_node_ids:
            try:
                payload = {
                    "query": mutation,
                    "variables": {
                        "input": {
                            "issueId": node_id
                        }
                    }
                }

                response = requests.post(
                    self.graphql_url,
                    headers=self._graphql_headers(),
                    json=payload
                )
                response.raise_for_status()
                result = response.json()

                # Check for GraphQL errors
                if 'errors' in result:
                    self.logger.warning(f"Error deleting issue {node_id}: {result['errors']}")

                # Add a small delay to respect rate limits
                time.sleep(0.5)

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error deleting issue {node_id}: {e}")

    def batch_delete_issues(self, issue_node_ids: List[str]) -> None:
        """
        Batch delete issues using GraphQL mutations.

        Args:
            issue_node_ids: List of issue node IDs to delete
        """
        # GraphQL mutation for deleting multiple issues
        mutation = """
        mutation DeleteIssues($input: [DeleteIssueInput!]!) {
            deleteIssues(input: $input) {
                clientMutationId
            }
        }
        """

        # Break issues into batches of 10 to avoid overwhelming the API
        batch_size = 10
        for i in range(0, len(issue_node_ids), batch_size):
            batch = issue_node_ids[i:i + batch_size]

            # Prepare input for mutation
            inputs = [{"issueId": node_id} for node_id in batch]

            payload = {
                "query": mutation,
                "variables": {"input": inputs}
            }

            try:
                response = requests.post(
                    self.graphql_url,
                    headers=self._graphql_headers(),
                    json=payload
                )
                response.raise_for_status()
                result = response.json()

                # Check for GraphQL errors
                if 'errors' in result:
                    raise Exception(f"GraphQL Error in batch delete: {result['errors']}")

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error in batch delete: {e}")
                raise


    def get_issue_node_id(self, repo_owner: str, repo_name: str, issue_number: int) -> str:
        """
        Retrieve the node ID for a specific issue using GraphQL.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            issue_number: Issue number

        Returns:
            Node ID of the issue
        """
        query = """
        query GetIssueNodeId($owner: String!, $repo: String!, $number: Int!) {
            repository(owner: $owner, name: $repo) {
                issue(number: $number) {
                    id
                }
            }
        }
        """

        variables = {
            "owner": repo_owner,
            "repo": repo_name,
            "number": issue_number
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

            return result['data']['repository']['issue']['id']

        except requests.exceptions.RequestException as e:
            self.logger.error(f"GraphQL Request Error: {e}")
            raise

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