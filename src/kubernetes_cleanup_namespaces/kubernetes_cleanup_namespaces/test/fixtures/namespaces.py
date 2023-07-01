import pytest

@pytest.fixture
def mock_ns_object(mock_kctl_object):
  class MockNamespaces:
    def __init__(self):
      self._kctl = mock_kctl_object
      pass
    def created_at(self, namespace):
      pass
    def delete(self, namespace):
      self._kctl.delete_namespace(namespace)
  return MockNamespaces()

@pytest.fixture
def mock_kctl_object():
  class MockKctl:
    def __init__(self):
      pass
    def delete_namespace(self, name):
      pass
  return MockKctl()
