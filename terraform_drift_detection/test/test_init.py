import logging

from terraform_drift_detection.init import setup_logging

def describe_setup_logging():
  def it_filters_out_username_password_from_url_logs(caplog):
    caplog.set_level(logging.INFO)
    setup_logging()
    logging.info('https://github:token@github.com')
    assert caplog.text == 'INFO: https://<FILTERED>@github.com\n'
