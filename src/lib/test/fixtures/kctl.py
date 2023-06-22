import json
import pytest

from lib.k8s_namespaces import Namespaces

@pytest.fixture
def mock_kctl(
  mock_kubectl_get_namespaces_json_object,
  mock_kubectl_get_pods_json_object,
  mock_kubectl_get_jobs_json_object
):
  class MockKctl:
    def __init__(self):
      pass
    def delete_pod(self, namespace, pod_name):
      pass
    def delete_job(self, namespace, job_name):
      pass
    def get_namespaces(self):
      return mock_kubectl_get_namespaces_json_object['items']
    def get_pods(self, namespace):
      return mock_kubectl_get_pods_json_object['items']
    def get_jobs(self, namespace):
      return mock_kubectl_get_jobs_json_object['items']
  return MockKctl()

# namespace fixtures

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
def mock_kubectl_get_namespaces_json_string(
  mock_kubectl_get_namespaces_json_object
):
  obj = mock_kubectl_get_namespaces_json_object
  return json.dumps(obj)

@pytest.fixture
def namespaces_obj(mock_kctl):
  return Namespaces(mock_kctl)


# pod fixtures

@pytest.fixture
def mock_kubectl_get_pods_json_object():
  return {
    'items': [
      {
        'metadata': {
          'name': 'pod1',
          'namespace': 'foo'
        },
        'status': {
          'startTime': '2023-05-17T00:00:00Z'
        }
      },
      {
        'metadata': {
          'name': 'pod2',
          'namespace': 'foo'
        },
        'status': {
          'startTime': '2023-05-19T00:00:00Z',
          'phase': 'Succeeded'
        }
      }
    ]
  }

@pytest.fixture
def mock_kubectl_get_pods_json_string(
  mock_kubectl_get_pods_json_object
):
  return json.dumps(mock_kubectl_get_pods_json_object)

# job fixtures

@pytest.fixture
def mock_kubectl_get_jobs_json_object():
  return {
    'items': [
      {
        'metadata': {
          'name': 'job1',
          'namespace': 'foo'
        },
        'status': {
          'completionTime': '2023-05-17T01:00:00Z',
          'conditions': [
            {
              'lastProbeTime': '2023-05-17T01:00:00Z',
              'lastTransitionTime': '2023-05-17T01:00:00Z',
              'status': 'True',
              'type': 'Complete'
            }
          ],
          'startTime': '2023-05-17T00:00:00Z',
          'succeeded': 1
        }
      },
      {
        'metadata': {
          'name': 'job2',
          'namespace': 'foo'
        },
        'status': {
          'active': 1,
          'startTime': '2023-05-17T02:00:00Z'
        }
      }
    ]
  }

@pytest.fixture
def mock_kubectl_get_jobs_json_string(
  mock_kubectl_get_jobs_json_object
):
  return json.dumps(mock_kubectl_get_jobs_json_object)
