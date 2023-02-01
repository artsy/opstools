import os
import pytest
import tempfile

from terraform_drift_detection.util import getenv, run_cmd

def describe_env():
  def it_gets():
    os.environ['REPOS'] = 'foo'
    repos, dummy = getenv()
    assert repos == ['foo']

def describe_run_cmd():
  def it_runs():
    cmd = 'echo foo'
    with tempfile.TemporaryDirectory() as tmpdir:
      os.chdir(tmpdir)
      os.makedirs('foo')
      output = run_cmd('ls', tmpdir)
    assert output.stdout == 'foo\n'
