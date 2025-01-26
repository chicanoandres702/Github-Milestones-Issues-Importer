from jsonschema import validate, exceptions
class JsonValidator:
    def __init__(self, logger):
        self.logger = logger
        self.milestone_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "state": {"type": "string", "enum": ["open", "closed"]},
                "description": {"type": "string"},
                "due_on": {"type": "string", "format": "date-time"}
            },
            "required": ["title"]
        }
        self.issue_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "labels": {
                    "type": "array",
                     "items": {
                       "type": "string"
                       }
                 },
               "tasks": {
                    "type": "array",
                    "items": {
                         "type": "string"
                       }
               }
            },
            "required": ["title"]
        }
    def validate_milestone_data(self, data):
        """Validates milestone data against the schema."""
        try:
          validate(instance=data, schema=self.milestone_schema)
        except exceptions.ValidationError as e:
            self.logger.error(f"Invalid milestone data: {data}. Error: {e}")
            raise exceptions.ValidationError(e)
    def validate_issue_data(self, data):
      """Validates issue data against the schema."""
      try:
          validate(instance=data, schema=self.issue_schema)
      except exceptions.ValidationError as e:
           self.logger.error(f"Invalid issue data: {data}. Error: {e}")
           raise exceptions.ValidationError(e)