import pytest

from lib.k8s_pods import Pods

from lib.test.fixtures.kctl import mock_kctl

@pytest.fixture
def pods_obj(mock_kctl):
  return Pods(mock_kctl, 'foo')
