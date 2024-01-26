import pytest

from lib.validations import (
  is_artsy_s3_bucket,
  is_artsy_staging_internal_hostname,
  is_artsy_production_internal_hostname,
  hostname_agrees_with_artsy_environment
)


def describe_is_artsy_s3_bucket():
  def it_returns_true_when_name_starts_with_artsy():
    assert is_artsy_s3_bucket('artsy-foo-bucket')
  def it_returns_false_when_name_does_not_start_with_artsy():
    assert not is_artsy_s3_bucket('foo-bucket')
  def it_returns_false_when_name_is_empty_string():
    assert not is_artsy_s3_bucket('')

def describe_is_artsy_staging_internal_hostname():
  def it_returns_true_when_name_is():
    assert is_artsy_staging_internal_hostname('foo.stg.artsy.systems')
  def it_returns_false_when_name_is_not():
    assert not is_artsy_staging_internal_hostname('foo.stg.artsy.system')

def describe_is_artsy_production_internal_hostname():
  def it_returns_true_when_name_is():
    assert is_artsy_production_internal_hostname('foo.prd.artsy.systems')
  def it_returns_false_when_name_is_not():
    assert not is_artsy_production_internal_hostname('foo.prd.artsy.system')

def describe_hostname_agrees_with_artsy_environment():
  def it_returns_true_when_env_is_staging_and_name_agrees():
    assert hostname_agrees_with_artsy_environment('foo.stg.artsy.systems', 'staging')
  def it_returns_false_when_env_is_staging_and_name_conflicts():
    assert not hostname_agrees_with_artsy_environment('foo.prd.artsy.systems', 'staging')
  def it_returns_true_when_env_is_production_and_name_agrees():
    assert hostname_agrees_with_artsy_environment('foo.prd.artsy.systems', 'production')
  def it_returns_false_when_env_is_production_and_name_conflicts():
    assert not hostname_agrees_with_artsy_environment('foo.stg.artsy.systems', 'production')
  def it_raises_on_unknown_env():
    with pytest.raises(Exception):
      hostname_agrees_with_artsy_environment('fooname', 'fooenv')
