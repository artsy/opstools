import logging
import re

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

def setup_logging(level):
  ''' configure root level logging '''
  logging.basicConfig(level=level)

def setup_sensitive_logging(level):
  ''' configure root level logging, with url filtering '''
  logging.basicConfig(level=level)
  format = '%(levelname)s: %(message)s'
  for handler in logging.root.handlers:
     handler.setFormatter(FilterOutSensitiveInfoFormatter(format))
