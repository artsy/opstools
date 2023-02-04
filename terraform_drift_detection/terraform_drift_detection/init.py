import logging
import re

from terraform_drift_detection.config import config

def init():
  ''' initialize everything for the app '''
  setup_logging()

class FilterOutSensitiveInfoFormatter(logging.Formatter):
  ''' filter out sensitive info from logs '''
  @staticmethod
  def _filter(log):
    try:
      # https://<sensitive>@foo.com... urls
      return re.sub(r':\/\/(.*?)\@', r'://<FILTERED>@', log)
    except:
      # exception's output includes the app log that triggered the exception.
      # since the app log may contain sensitive data, silence the exception.
      print('Error: FilterOutSensitiveInfoFormatter._filter() raised an exception.')
      exit(1)

  def format(self, record):
    formatted_log = logging.Formatter.format(self, record)
    return self._filter(formatted_log)

def setup_logging():
  ''' setup app wide logging '''
  logging.basicConfig(level=logging.INFO)
  format = '%(levelname)s: %(message)s'
  for handler in logging.root.handlers:
     handler.setFormatter(FilterOutSensitiveInfoFormatter(format))
