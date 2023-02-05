import pytest

from subprocess import CompletedProcess

@pytest.fixture
def mock_clone_failed():
  def mock_run_cmd(cmd, dir):
    return_values = {
      'git clone https://github:footoken@github.com/artsy/foorepo.git': CompletedProcess('git clone', 1),
    }
    return return_values[cmd]
  return mock_run_cmd

@pytest.fixture
def mock_clone_success():
  def mock_run_cmd(cmd, dir):
    return_values = {
      'git clone https://github:footoken@github.com/artsy/foorepo.git': CompletedProcess('git clone', 0),
    }
    return return_values[cmd]
  return mock_run_cmd

@pytest.fixture
def mock_init_failed():
  def mock_run_cmd(cmd, dir):
    return_values = {
      'terraform init': CompletedProcess('tf init', 1),
    }
    return return_values[cmd]
  return mock_run_cmd

@pytest.fixture
def mock_plan_drift():
  def mock_run_cmd(cmd, dir):
    return_values = {
      'terraform init': CompletedProcess('tf init', 0),
      'terraform plan -detailed-exitcode': CompletedProcess('tf plan', 2),
    }
    return return_values[cmd]
  return mock_run_cmd

@pytest.fixture
def mock_plan_no_drift():
  def mock_run_cmd(cmd, dir):
    return_values = {
      'terraform init': CompletedProcess('tf init', 0),
      'terraform plan -detailed-exitcode': CompletedProcess('tf plan', 0),
    }
    return return_values[cmd]
  return mock_run_cmd

@pytest.fixture
def mock_plan_unknown():
  def mock_run_cmd(cmd, dir):
    return_values = {
      'terraform init': CompletedProcess('tf init', 0),
      'terraform plan -detailed-exitcode': CompletedProcess('tf plan', 1),
    }
    return return_values[cmd]
  return mock_run_cmd
