import json
import pytest

from lib.k8s_namespaces import \
  Namespaces

@pytest.fixture
def mock_kctl(mock_kubectl_get_namespaces_json_object):
  class MockKctl():
    def __init__(self):
      pass
    def get_namespaces(self):
      return mock_kubectl_get_namespaces_json_object['items']
  return MockKctl()

@pytest.fixture
def mock_kubectl_get_namespaces_json_object():
  obj = {
    'items': [
        { 'metadata': {
            'name': 'namespace1',
            'creationTimestamp': '2023-04-12T21:24:33Z'
          }
        },
        { 'metadata': {
            'name': 'namespace2',
            'creationTimestamp': '2023-04-13T21:24:33Z'
          }
        }
    ]
  }
  return obj

@pytest.fixture
def mock_kubectl_get_namespaces_json_string(mock_kubectl_get_namespaces_json_object):
  obj = mock_kubectl_get_namespaces_json_object
  return json.dumps(obj)

@pytest.fixture
def namespaces_obj(mock_kctl):
  return Namespaces(mock_kctl)
