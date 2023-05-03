import pytest

from lib.k8s_namespaces import \
  Namespaces

from lib.test.fixtures.kctl import \
  mock_kctl

@pytest.fixture
def namespaces_obj(mock_kctl):
  return Namespaces(mock_kctl)
