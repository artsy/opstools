import lib.sanitizers

from lib.sanitizers import (
  config_secret_sanitizer,
  config_secret_sanitizer_artsy,
  config_secret_sanitizer_eso
)


def describe_config_secret_sanitizer():
  def it_runs_all_sanitizers(mocker):
    mocker.patch('lib.sanitizers.config_secret_sanitizer_artsy').return_value = 'artsy_sanitized'
    spy1 = mocker.spy(lib.sanitizers, 'config_secret_sanitizer_artsy')
    mocker.patch('lib.sanitizers.config_secret_sanitizer_eso').return_value = 'eso_sanitized'
    spy2 = mocker.spy(lib.sanitizers, 'config_secret_sanitizer_eso')
    sanitized_value = config_secret_sanitizer('foo')
    spy1.assert_has_calls([
      mocker.call('foo')
    ])
    spy2.assert_has_calls([
      mocker.call('artsy_sanitized')
    ])
    assert sanitized_value == 'eso_sanitized'

def describe_config_secret_sanitizer_artsy():
  def it_removes_surrounding_quotes():
    assert config_secret_sanitizer_artsy('"foo"') == 'foo'

def describe_config_secret_sanitizer_eso():
  def it_adds_double_quotes_when_special_yaml_char():
    assert config_secret_sanitizer_eso('*foo') == '"*foo"'
  def it_returns_same_string_otherwise():
    assert config_secret_sanitizer_eso('foo') == 'foo'
