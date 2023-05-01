import logging

from lib.logging import setup_logging

def describe_setup_logging():
  def it_sets_the_correct_level():
    # cannot be tested due to pytest overriding root log level
    # https://github.com/pytest-dev/pytest/issues/9989
    #
    #setup_logging(logging.INFO)
    #assert logging.root.level == logging.INFO
    pass
