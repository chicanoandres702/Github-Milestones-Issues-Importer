import requests
import json
import time

class GitHubClient:
    def __init__(self, access_token, logger, auth_manager):
        self.access_token = access_token
        self.logger = logger
        self.auth_manager = auth_manager
        self.headers = {
                "Authorization": f"token {self.access_token}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28"
                }

    def _log_request(self, method, url, headers, data=None):
      log_message = f"Making {method} request to: {url}\n"
      log_message += f"Headers: {headers}\n"
      if data:
          log_message += f"Data: {json.dumps(data, indent=2)}\n"
      self.logger.info(log_message)

    def _handle_rate_limit(self, response):
        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
        self.logger.info(f"Rate Limit Remaining: {remaining}")
        if remaining == 0:
          wait_time = max(0, reset_time - int(time.time()))
          self.logger.warning(f"Rate limit exceeded. Waiting {wait_time} seconds before retrying.")
          time.sleep(wait_time)
          return True
        return False

    def _sleep(self):
        time.sleep(1)

    def _refresh_token_and_retry(self, method, url, headers, data=None):
      self.logger.info("Access token has likely expired, attempting to refresh the token and retrying request.")
      if self.auth_manager.refresh_access_token():
          headers["Authorization"] = f"token {self.auth_manager.access_token}"
          self.headers["Authorization"] = f"token {self.auth_manager.access_token}"
          return self._make_request(method, url, headers, data)
      else:
          self.logger.error("Unable to refresh the access token. Please log in again.")
          return None


    def _make_request(self, method, url, headers, data=None):
            try:
              if method == "GET":
                  response = requests.get(url, headers=headers)
              elif method == "POST":
                  response = requests.post(url, headers=headers, json=data)
              elif method == "DELETE":
                  response = requests.delete(url, headers=headers)
              else:
                  self.logger.error(f"Invalid http method of {method}")
                  return None

              response.raise_for_status()
              return response
            except requests.exceptions.RequestException as e:
              if e.response and e.response.status_code == 403:
                   response = self._refresh_token_and_retry(method, url, headers, data)
                   return response
              self.logger.error(f"Request failed: {e}")
              return None

    def check_access_token(self):
        """
        Checks the validity of the access token.

        Returns:
            int: HTTP status code of the user API request.

        """
        url = "https://api.github.com/user"
        self._log_request("GET", url, self.headers)
        response = self._make_request("GET", url, self.headers)

        if response:
          if self._handle_rate_limit(response):
             response =  self._make_request("GET", url, self.headers)
          return response.status_code
        else:
           return None

    def get_user_repos(self):
        url = "https://api.github.com/user/repos"
        self._log_request("GET", url, self.headers)
        response = self._make_request("GET", url, self.headers)
        if response:
            if self._handle_rate_limit(response):
               response = self._make_request("GET", url, self.headers)
            return response.json()
        else:
          return None

    def get_milestones(self, repo_owner, repo_name):
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/milestones"
        self._log_request("GET", url, self.headers)
        response = self._make_request("GET", url, self.headers)
        if response:
          if self._handle_rate_limit(response):
            response =  self._make_request("GET", url, self.headers)
          return response.json()
        else:
            return None

    def create_milestone(self, repo_owner, repo_name, milestone_data):
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/milestones"
        self._log_request("POST", url, self.headers, milestone_data)
        response = self._make_request("POST", url, self.headers, milestone_data)
        if response:
          if self._handle_rate_limit(response):
                response =  self._make_request("POST", url, self.headers, milestone_data)
          self.logger.info(f"Successfully created milestone: {milestone_data['title']} ")
          return response.json()
        else:
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
        url = "https://api.github.com/graphql"  # GitHub GraphQL API endpoint
        query = """
                mutation DeleteIssue($issueId: ID!, $clientMutationId: String!) {
                    deleteIssue(input: {issueId: $issueId, clientMutationId: $clientMutationId}) {
                        clientMutationId
                    }
                }
             """
        variables = {"issueId": f"I_{issue_number}", "clientMutationId": "delete-issue"}
        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        data = {"query": query, "variables": variables}

        self._log_request("POST", url, headers, data)
        response = self._make_request("POST", url, headers, data)

        if response:
             if self._handle_rate_limit(response):
                 response = self._make_request("POST", url, headers, data)
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