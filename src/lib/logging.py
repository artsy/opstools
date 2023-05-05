import logging

def setup_logging(level):
  ''' configure root level logging '''
  logging.basicConfig(level=level)
  format = '%(levelname)s: %(message)s'
