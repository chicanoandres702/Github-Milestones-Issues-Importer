import json
from github_importer.github_api.models import Milestone, Issue

class DataImporter:
    """Handles importing of data from JSON files."""

    def __init__(self, github_client, logger):
        self.github_client = github_client
        self.logger = logger

    def import_data(self, repo_owner, repo_name, import_file):
      """Imports milestones and issues from a JSON file."""
      try:
          with open(import_file, "r") as f:
              data = json.load(f)

          for milestone_data in data:
              milestone = Milestone(**milestone_data)
              milestone_response = self.github_client.create_milestone(repo_owner, repo_name, milestone.__dict__)

              if milestone_response:
                  milestone_id = milestone_response["id"]
                  for issue_data in milestone_data.get("issues", []):
                    issue = Issue(**issue_data, milestone = milestone_id)
                    self.github_client.create_issue(repo_owner, repo_name, issue.__dict__)
          self.logger.info("Import process completed")
          return True
      except FileNotFoundError:
          self.logger.error(f"Error: File not found: {import_file}")
          return False
      except json.JSONDecodeError:
          self.logger.error(f"Error: Invalid JSON format in {import_file}")
          return False
      except Exception as e:
          self.logger.error(f"An error occurred during import process: {e}")
          return False