import pytest

from subprocess import CompletedProcess
from terraform_drift_detection.terraform import find_tf_dirs

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
