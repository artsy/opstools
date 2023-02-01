import pytest

from subprocess import CompletedProcess
from terraform_drift_detection.terraform import find_tf_dirs, tf_in_repo_dir

def describe_find_tf_dirs():
  def it_finds(mocker):
    files = [
      '/foo/foo/foo.tf',
      '/foo/bar/bar.tf'
    ]
    tf_dirs = [
      '/foo/bar',
      '/foo/foo'
    ]
    mocker.patch('glob.glob', return_value=files)
    mocker.patch('os.path.isfile', return_value=True)
    assert find_tf_dirs('foo') == tf_dirs

def describe_tf_in_repo_dir():
  def it_aborts_on_failed_init(mocker):
    tf_init_completed_process = CompletedProcess('tf init', 1)
    tf_plan_completed_process = CompletedProcess('tf plan', 0)
    mocker.patch('terraform_drift_detection.terraform.run_cmd').side_effect = [tf_init_completed_process, tf_plan_completed_process]
    with pytest.raises(SystemExit):
      tf_in_repo_dir('dir1')
  def it_aborts_on_failed_plan(mocker):
    tf_init_completed_process = CompletedProcess('tf init', 0)
    tf_plan_completed_process = CompletedProcess('tf plan', 1)
    mocker.patch('terraform_drift_detection.terraform.run_cmd').side_effect = [tf_init_completed_process, tf_plan_completed_process]
    with pytest.raises(SystemExit):
      tf_in_repo_dir('dir1')
  def it_exits_happy_on_success(mocker):
    tf_init_completed_process = CompletedProcess('tf init', 0)
    tf_plan_completed_process = CompletedProcess('tf plan', 0)
    mocker.patch('terraform_drift_detection.terraform.run_cmd').side_effect = [tf_init_completed_process, tf_plan_completed_process]
    tf_in_repo_dir('dir1')
