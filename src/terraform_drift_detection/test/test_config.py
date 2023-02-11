import pytest

from terraform_drift_detection.config import AppConfig, AppConfigError, config, parse_reposdirs, validate

def describe_AppConfig():
  def it_raises_value_error():
    with pytest.raises(ValueError):
      AppConfig({})
  def it_raises_appconfig_error():
    with pytest.raises(AppConfigError):
      AppConfig({'REPOSDIRS': 'foorepo:foodir', 'GITHUB_TOKEN': ''})
  def it_passes_on_good_env():
      AppConfig({'REPOSDIRS': 'foorepo:foodir', 'GITHUB_TOKEN': 'footoken'})

def describe_config():
  def it_is_initialized():
    assert config.repos_dirs == {'foorepo': ['foodir']}
    assert config.github_token == 'footoken'

def describe_parse_reposdirs():
  def it_parses():
    reposdirs = 'repo1:dir1,repo1:dir2,repo2:dir1'
    assert parse_reposdirs(reposdirs) == {
      'repo1': ['dir1', 'dir2'],
      'repo2': ['dir1']
    }

def describe_validate():
  def it_returns_true_for_good_values():
    assert validate('footoken', 'foorepo:foodir', {'foorepo': ['foodir']}) == True
  def it_returns_false_for_empty_token():
    assert validate('', 'foorepo:foodir', {'foorepo': ['foodir']}) == False
  def it_returns_false_for_empty_reposdirs():
    assert validate('footoken', '', {'foorepo': ['foodir']}) == False
  def it_returns_false_for_empty_repos_dirs_dict():
    assert validate('footoken', 'foorepo:foodir', {}) == False
  def it_returns_false_for_repos_dirs_with_empty_dir_list():
    assert validate('footoken', 'foorepo:foodir', {'foorepo': []}) == False
  def it_returns_false_for_repos_dirs_with_blank_dir():
    assert validate('footoken', 'foorepo:foodir', {'foorepo': ['foodir', '']}) == False
