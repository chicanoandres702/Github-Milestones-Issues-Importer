import requests

class GitHubClient:
    def __init__(self, access_token, logger):
        self.access_token = access_token
        self.logger = logger

        self.headers = {
                "Authorization": f"token {self.access_token}",
                "Accept": "application/vnd.github.v3+json"
                }

    def check_access_token(self):
        """
        Checks the validity of the access token.

        Returns:
            int: HTTP status code of the user API request.

        """
        url = "https://api.github.com/user"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.status_code
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error checking access token: {e}")
            return e.response.status_code if e.response else None


    def get_user_repos(self):
        url = "https://api.github.com/user/repos"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"An error has occurred getting user repos: {e}")
            raise Exception(e)

    def get_milestones(self, repo_owner, repo_name):
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/milestones"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"An error has occurred getting milestones: {e}")
            raise Exception(e)
    def create_milestone(self, repo_owner, repo_name, milestone_data):
         url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/milestones"
         try:
             response = requests.post(url, headers=self.headers, json=milestone_data)
             response.raise_for_status()
             self.logger.info(f"Successfully created milestone: {milestone_data['title']} ")
             return response.json()
         except requests.exceptions.RequestException as e:
              self.logger.error(f"An error has occurred creating the milestone {milestone_data['title']}: {e}")
              raise Exception(e)