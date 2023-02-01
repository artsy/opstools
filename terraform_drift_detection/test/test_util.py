import os
import pytest
import tempfile

from terraform_drift_detection.util import abort_on_nonzero_exit, getenv, run_cmd

def describe_abort_on_nonzero_exit():
  def it_aborts_on_nonzero():
    with pytest.raises(SystemExit):
      abort_on_nonzero_exit('foo', 1)
  def it_exits_happy_on_zero():
    abort_on_nonzero_exit('foo', 0)

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
