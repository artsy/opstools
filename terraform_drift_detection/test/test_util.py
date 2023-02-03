import os
import tempfile

from terraform_drift_detection.util import getenv, run_cmd, validate, validate_repo_name, validate_repo_names

def describe_getenv():
  def it_gets():
    os.environ['REPO_NAMES'] = 'foo'
    repos, dummy = getenv()
    assert repos == ['foo']

def describe_run_cmd():
  def it_runs():
    with tempfile.TemporaryDirectory() as tmpdir:
      os.chdir(tmpdir)
      os.makedirs('foo')
      output = run_cmd('ls', tmpdir)
    assert output.stdout == 'foo\n'

def describe_validate_repo_name():
  def it_validates_non_empty_string():
    assert validate_repo_name('foo') == True
  def it_invalidates_empty_string():
    assert validate_repo_name('') == False

def describe_validate_repo_names():
  def it_invalidates_empty_list():
    assert validate_repo_names([]) == False
  def it_invalidates_list_if_empty_string_present():
    assert validate_repo_names(['']) == False
    assert validate_repo_names(['foo', '']) == False
  def it_validates_list_if_no_empty_strings():
    assert validate_repo_names(['foo', 'bar']) == True

def describe_validate():
  def it_invalidates_bad_repo_names():
    assert validate([], 'foo') == False
    assert validate([''], 'foo') == False
  def it_validates_good_repo_names():
    assert validate(['foo'], 'bar') == True
  def it_invalidates_empty_github_token():
    assert validate(['foo'], '') == False
  def it_validates_nonempty_github_token():
    assert validate(['foo'], 'bar') == True
