import os
import tempfile

from terraform_drift_detection.util import run_cmd

def describe_run_cmd():
  def it_runs():
    with tempfile.TemporaryDirectory() as tmpdir:
      os.chdir(tmpdir)
      os.makedirs('foo')
      output = run_cmd('ls', tmpdir)
    assert output.stdout == 'foo\n'
