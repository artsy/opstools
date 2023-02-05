import pytest

from terraform_drift_detection.config import AppConfig, AppConfigError, config, validate

def describe_AppConfig():
  def it_raises_on_bad_env():
    with pytest.raises(AppConfigError):
      AppConfig({})
  def it_is_happy_on_good_env():
      AppConfig({'REPO_NAMES': 'foorepo', 'GITHUB_TOKEN': 'footoken'})

def describe_config():
  def it_is_initialized():
    assert config.repos == ['foorepo']
    assert config.github_token == 'footoken'

def describe_validate():
  def it_returns_true_for_good_values():
    assert validate('footoken', 'foorepo', ['foorepo']) == True
  def it_returns_false_for_empty_token():
    assert validate('', 'foorepo', ['foorepo']) == False
  def it_returns_false_for_empty_repo_names():
    assert validate('footoken', '', ['foorepo']) == False
  def it_returns_false_for_empty_repo_list():
    assert validate('footoken', 'foorepo', []) == False
  def it_returns_false_for_repo_list_with_empty_strings():
    assert validate('footoken', 'foorepo', ['foorepo', '']) == False
