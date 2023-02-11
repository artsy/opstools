import os

import terraform_drift_detection.terraform

from functools import reduce
from terraform_drift_detection.config import config
from terraform_drift_detection.terraform import check_dir, check_repo, check_repos, check_tf_dir, find_tf_dirs
from terraform_drift_detection.util import Drift
from test.fixtures.terraform import \
  expected_results, \
  mock_clone_failed, \
  mock_clone_success, \
  mock_init_failed, \
  mock_multiple_repo_dir_results, \
  mock_plan_drift, \
  mock_plan_no_drift, \
  mock_plan_unknown

def describe_check_dir():
  def it_returns_correct_check_tf_dir_results(mocker):
    mocker.patch('terraform_drift_detection.terraform.find_tf_dirs', return_value=['dir1', 'dir2', 'dir3'])
    mocker.patch('terraform_drift_detection.terraform.check_tf_dir').side_effect = [Drift.NODRIFT, Drift.DRIFT, Drift.UNKNOWN]
    results = check_dir('foodir')
    assert results == [Drift.NODRIFT, Drift.DRIFT, Drift.UNKNOWN]

def describe_check_repo():
  def it_returns_unknown_if_clone_failed(mocker, mock_clone_failed):
    mocker.patch('terraform_drift_detection.terraform.run_cmd').side_effect = mock_clone_failed
    spy = mocker.spy(terraform_drift_detection.terraform, 'run_cmd')
    results = check_repo('foorepo', 'foobasedir')
    assert spy.call_count == 1
    spy.assert_has_calls([mocker.call('git clone https://github:footoken@github.com/artsy/foorepo.git', 'foobasedir')])
    assert results == [Drift.UNKNOWN]
  def it_returns_correct_check_dir_results(expected_results, mocker, mock_clone_success, mock_multiple_repo_dir_results):
    mocker.patch('terraform_drift_detection.terraform.run_cmd').side_effect = mock_clone_success
    mocker.patch('terraform_drift_detection.terraform.check_dir').side_effect = mock_multiple_repo_dir_results
    mocker.patch.object(config, 'repos_dirs', {'foorepo': ['dir1', 'dir2', 'dir3']})
    run_cmd_spy = mocker.spy(terraform_drift_detection.terraform, 'run_cmd')
    check_dir_spy = mocker.spy(terraform_drift_detection.terraform, 'check_dir')
    results = check_repo('foorepo', 'foobasedir')
    assert run_cmd_spy.call_count == 1
    assert check_dir_spy.call_count == 3
    run_cmd_spy.assert_has_calls([mocker.call('git clone https://github:footoken@github.com/artsy/foorepo.git', 'foobasedir')])
    check_dir_spy.assert_has_calls(
      [
        mocker.call('foobasedir/foorepo/dir1'),
        mocker.call('foobasedir/foorepo/dir2'),
        mocker.call('foobasedir/foorepo/dir3')
      ]
    )
    assert results == expected_results

def describe_check_repos():
  def it_returns_correct_check_repo_results(expected_results, mocker, mock_multiple_repo_dir_results):
    mocker.patch('terraform_drift_detection.terraform.check_repo').side_effect = mock_multiple_repo_dir_results
    mocker.patch.object(config, 'repos_dirs', {'repo1': ['dir1'], 'repo2':['dir2'], 'repo3':['dir3']})
    results = check_repos()
    assert results == expected_results

def describe_check_tf_dir():
  def it_returns_unknown_if_init_failed(mocker, mock_init_failed):
    mocker.patch('terraform_drift_detection.terraform.run_cmd').side_effect = mock_init_failed
    spy = mocker.spy(terraform_drift_detection.terraform, 'run_cmd')
    result = check_tf_dir('foodir')
    assert spy.call_count == 1
    spy.assert_has_calls([mocker.call('terraform init', 'foodir')])
    assert result == Drift.UNKNOWN
  def it_returns_no_drift_if_plan_returned_zero(mocker, mock_plan_no_drift):
    mocker.patch('terraform_drift_detection.terraform.run_cmd').side_effect = mock_plan_no_drift
    spy = mocker.spy(terraform_drift_detection.terraform, 'run_cmd')
    result = check_tf_dir('foodir')
    assert spy.call_count == 2
    spy.assert_has_calls([mocker.call('terraform init', 'foodir'), mocker.call('terraform plan -detailed-exitcode', 'foodir')])
    assert result == Drift.NODRIFT
  def it_returns_drift_if_plan_returned_two(mocker, mock_plan_drift):
    mocker.patch('terraform_drift_detection.terraform.run_cmd').side_effect = mock_plan_drift
    spy = mocker.spy(terraform_drift_detection.terraform, 'run_cmd')
    result = check_tf_dir('foodir')
    assert spy.call_count == 2
    spy.assert_has_calls([mocker.call('terraform init', 'foodir'), mocker.call('terraform plan -detailed-exitcode', 'foodir')])
    assert result == Drift.DRIFT
  def it_returns_unknown_if_plan_returned_something_else(mocker, mock_plan_unknown):
    mocker.patch('terraform_drift_detection.terraform.run_cmd').side_effect = mock_plan_unknown
    spy = mocker.spy(terraform_drift_detection.terraform, 'run_cmd')
    result = check_tf_dir('foodir')
    assert spy.call_count == 2
    spy.assert_has_calls([mocker.call('terraform init', 'foodir'), mocker.call('terraform plan -detailed-exitcode', 'foodir')])
    assert result == Drift.UNKNOWN

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