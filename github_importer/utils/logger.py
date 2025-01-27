import logging
import datetime
class Logger:
    def __init__(self, name):
      self.logger = logging.getLogger(name)
      self.logger.setLevel(logging.INFO)

      formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

      ch = logging.StreamHandler()
      ch.setFormatter(formatter)
      self.logger.addHandler(ch)

    def set_handler(self, handler):
        self.handler = handler

    def addHandler(self, handler):
        self.set_handler(handler)
        return self

    def info(self, message):
        self.logger.info(message)
    def error(self, message):
        self.logger.error(message)