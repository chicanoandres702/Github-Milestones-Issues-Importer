import os
import json
class FileHandler:
  def __init__(self, base_dir=""):
    self.base_dir = base_dir

  def get_file_path(self, file_name, folder):
    """
    Returns the full path to a file within the data directory.
    """
    data_dir = os.path.join(self.base_dir, "data", folder)
    os.makedirs(data_dir, exist_ok=True)  # Creates directory if it doesn't exist
    return os.path.join(data_dir, file_name)

  def write_file(self, data, file_path):
    try:
      with open(file_path, 'w') as file:
         json.dump(data, file, indent=4)

    except Exception as e:
       raise Exception(e)