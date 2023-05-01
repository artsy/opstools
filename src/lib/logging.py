import logging

def setup_logging(level):
  ''' setup app wide logging '''
  logging.basicConfig(level=level)
  format = '%(levelname)s: %(message)s'
