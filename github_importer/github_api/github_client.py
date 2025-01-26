import requests
import json


class GitHubClient:
    """Encapsulates interactions with the GitHub API."""

    def __init__(self, access_token, logger):
        self.access_token = access_token
        self.logger = logger
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.access_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def _handle_response(self, response, success_message):
        """Handles API responses, including error handling and logging"""
        try:
            response.raise_for_status()  # Raise HTTPError for bad responses
            self.logger.info(success_message)
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API Error: {response.status_code} - {e} - {response.text}")
            return None

    def create_milestone(self, repo_owner, repo_name, milestone_data):
        """Creates a milestone in the repository."""
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/milestones"
        response = requests.post(url, headers=self.headers, data=json.dumps(milestone_data))
        return self._handle_response(response, f"Milestone '{milestone_data['title']}' created successfully!")

    def create_issue(self, repo_owner, repo_name, issue_data):
        """Creates an issue in the repository."""
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/issues"

        # Construct issue body
        issue_body = ""
        if "tasks" in issue_data:
            issue_body += "## Tasks:\n\n"
            for task in issue_data["tasks"]:
                issue_body += f"- [ ] {task}\n"
            issue_body += "\n"

        if "description" in issue_data:
            issue_body += f"## Description:\n\n{issue_data['description']}\n\n"

        if "overview" in issue_data:
            issue_body += f"## Overview:\n\n{issue_data['overview']}\n\n"

        issue_data["body"] = issue_body

        response = requests.post(url, headers=self.headers, data=json.dumps(issue_data))

        issue_data_response = self._handle_response(response, f"Issue '{issue_data['title']}' created successfully!")
        if issue_data_response:
            issue_number = issue_data_response["number"]

            if "labels" in issue_data:
                self.add_labels_to_issue(repo_owner, repo_name, issue_number, issue_data["labels"])
            if "assignees" in issue_data:
                self.add_assignees_to_issue(repo_owner, repo_name, issue_number, issue_data["assignees"])
            if "comments" in issue_data:
                for comment in issue_data["comments"]:
                    self.add_comment_to_issue(repo_owner, repo_name, issue_number, comment)

    def add_labels_to_issue(self, repo_owner, repo_name, issue_number, labels):
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/issues/{issue_number}/labels"
        response = requests.post(url, headers=self.headers, data=json.dumps(labels))
        self._handle_response(response, f"Labels added to issue {issue_number} successfully!")

    def add_assignees_to_issue(self, repo_owner, repo_name, issue_number, assignees):
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/issues/{issue_number}/assignees"
        response = requests.post(url, headers=self.headers, data=json.dumps({"assignees": assignees}))
        self._handle_response(response, f"Assignees added to issue {issue_number} successfully!")

    def add_comment_to_issue(self, repo_owner, repo_name, issue_number, comment):
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/issues/{issue_number}/comments"
        response = requests.post(url, headers=self.headers, data=json.dumps({"body": comment}))
        self._handle_response(response, f"Comment added to issue {issue_number} successfully!")