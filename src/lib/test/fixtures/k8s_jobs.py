import pytest

from lib.k8s_jobs import Jobs

from lib.test.fixtures.kctl import mock_kctl

@pytest.fixture
def jobs_obj(mock_kctl):
  return Jobs(mock_kctl, 'foo')
