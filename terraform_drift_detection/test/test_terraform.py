from terraform_drift_detection.terraform import check_dir, check_repo, find_tf_dirs
from terraform_drift_detection.util import Drift

def describe_check_dir():
  def it_returns_unknown_if_init_failed():
    pass
  def it_returns_no_drift_if_plan_returned_zero():
    pass
  def it_returns_drift_if_plan_returned_two():
    pass
  def it_returns_unknown_if_plan_returned_something_else():
    pass

def describe_check_repo():
  def it_returns_unknown_if_clone_failed():
    pass
  def it_returns_correct_check_dir_results():
    pass

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
