import pytest

from subprocess import CompletedProcess
from terraform_drift_detection.git import clone_repo

def describe_clone_repo():
  def it_aborts_on_failed_clone(mocker):
    foo_completed_process = CompletedProcess('foo', 1)
    mocker.patch('terraform_drift_detection.git.run_cmd', return_value=foo_completed_process)
    with pytest.raises(SystemExit):
      clone_repo('foo', 'dir1')
  def it_exits_happy_on_success(mocker):
    foo_completed_process = CompletedProcess('foo', 0)
    mocker.patch('terraform_drift_detection.git.run_cmd', return_value=foo_completed_process)
    clone_repo('foo', 'dir1')
