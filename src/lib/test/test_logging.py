import logging

from lib.logging import (
  setup_logging,
  setup_sensitive_logging
)

def describe_setup_logging():
  def it_sets_the_correct_level():
    # cannot be tested due to pytest overriding root log level
    # https://github.com/pytest-dev/pytest/issues/9989
    #
    #setup_logging(logging.INFO)
    #assert logging.root.level == logging.INFO
    pass

def describe_setup_sensitive_logging():
  def it_filters_out_username_password_from_url_logs(caplog):
    caplog.set_level(logging.INFO)
    setup_sensitive_logging(logging.INFO)
    logging.info('https://github:token@github.com')
    assert caplog.text == 'INFO: https://<FILTERED>@github.com\n'
