import os

import terraform_drift_detection.terraform

from functools import reduce
from terraform_drift_detection.config import config
from terraform_drift_detection.terraform import check_dir, check_repo, check_repos, find_tf_dirs
from terraform_drift_detection.util import Drift
from test.fixtures.terraform import \
  mock_clone_failed, \
  mock_clone_success, \
  mock_init_failed, \
  mock_plan_drift, \
  mock_plan_no_drift, \
  mock_plan_unknown

def describe_check_dir():
  def it_returns_unknown_if_init_failed(mocker, mock_init_failed):
    mocker.patch('terraform_drift_detection.terraform.run_cmd').side_effect = mock_init_failed
    spy = mocker.spy(terraform_drift_detection.terraform, 'run_cmd')
    result = check_dir('foodir')
    assert spy.call_count == 1
    spy.assert_has_calls([mocker.call('terraform init', 'foodir')])
    assert result == Drift.UNKNOWN
  def it_returns_no_drift_if_plan_returned_zero(mocker, mock_plan_no_drift):
    mocker.patch('terraform_drift_detection.terraform.run_cmd').side_effect = mock_plan_no_drift
    spy = mocker.spy(terraform_drift_detection.terraform, 'run_cmd')
    result = check_dir('foodir')
    assert spy.call_count == 2
    spy.assert_has_calls([mocker.call('terraform init', 'foodir'), mocker.call('terraform plan -detailed-exitcode', 'foodir')])
    assert result == Drift.NODRIFT
  def it_returns_drift_if_plan_returned_two(mocker, mock_plan_drift):
    mocker.patch('terraform_drift_detection.terraform.run_cmd').side_effect = mock_plan_drift
    spy = mocker.spy(terraform_drift_detection.terraform, 'run_cmd')
    result = check_dir('foodir')
    assert spy.call_count == 2
    spy.assert_has_calls([mocker.call('terraform init', 'foodir'), mocker.call('terraform plan -detailed-exitcode', 'foodir')])
    assert result == Drift.DRIFT
  def it_returns_unknown_if_plan_returned_something_else(mocker, mock_plan_unknown):
    mocker.patch('terraform_drift_detection.terraform.run_cmd').side_effect = mock_plan_unknown
    spy = mocker.spy(terraform_drift_detection.terraform, 'run_cmd')
    result = check_dir('foodir')
    assert spy.call_count == 2
    spy.assert_has_calls([mocker.call('terraform init', 'foodir'), mocker.call('terraform plan -detailed-exitcode', 'foodir')])
    assert result == Drift.UNKNOWN

def describe_check_repo():
  def it_returns_unknown_if_clone_failed(mocker, mock_clone_failed):
    mocker.patch('terraform_drift_detection.terraform.run_cmd').side_effect = mock_clone_failed
    spy = mocker.spy(terraform_drift_detection.terraform, 'run_cmd')
    results = check_repo('foorepo', 'foodir')
    assert spy.call_count == 1
    spy.assert_has_calls([mocker.call('git clone https://github:footoken@github.com/artsy/foorepo.git', 'foodir')])
    assert results == [Drift.UNKNOWN]
  def it_returns_correct_check_dir_results(mocker, mock_clone_success):
    mocker.patch('terraform_drift_detection.terraform.run_cmd').side_effect = mock_clone_success
    mocker.patch('terraform_drift_detection.terraform.find_tf_dirs', return_value=['dir1', 'dir2', 'dir3'])
    mocker.patch('terraform_drift_detection.terraform.check_dir').side_effect = [Drift.NODRIFT, Drift.DRIFT, Drift.UNKNOWN]
    run_cmd_spy = mocker.spy(terraform_drift_detection.terraform, 'run_cmd')
    check_dir_spy = mocker.spy(terraform_drift_detection.terraform, 'check_dir')
    result = check_repo('foorepo', 'foodir')
    assert run_cmd_spy.call_count == 1
    assert check_dir_spy.call_count == 3
    run_cmd_spy.assert_has_calls([mocker.call('git clone https://github:footoken@github.com/artsy/foorepo.git', 'foodir')])
    check_dir_spy.assert_has_calls([mocker.call('dir1'), mocker.call('dir2'), mocker.call('dir3')])
    assert result == [Drift.NODRIFT, Drift.DRIFT, Drift.UNKNOWN]

def describe_check_repos():
  def it_returns_correct_check_repo_results(mocker):
    all_results = [
      [Drift.NODRIFT],
      [Drift.NODRIFT, Drift.DRIFT],
      [Drift.NODRIFT, Drift.DRIFT, Drift.UNKNOWN],
    ]
    mocker.patch('terraform_drift_detection.terraform.check_repo').side_effect = all_results
    mocker.patch.object(config, 'repos', ['foo', 'bar', 'baz'])
    results = check_repos()
    assert results == reduce(lambda x, y: x + y, all_results)

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
