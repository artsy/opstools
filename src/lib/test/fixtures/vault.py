import pytest

@pytest.fixture
def mock_exception_function():
  def raise_exception():
    raise Exception
  return raise_exception

@pytest.fixture
def mock_hvac_client_class():
  class MockClient():
    def __init__(self, url=None, token=None):
      self.secrets = MockSecrets()
  return MockClient

class MockSecrets():
  def __init__(self):
    self.kv = MockKV()

class MockKV():
  def __init__(self):
    self.v2 = MockV2()
  def read_secret_version(self, path, mount_point):
    response = {
      'data': {
        'data': {
          'fookey': 'foovalue'
        }
      }
    }
    return response

class MockV2():
  def __init__(self):
    pass
  def list_secrets(self, path, mount_point):
    return ['fookey', 'barkey']
  def create_or_update_secret(self, path, secret, mount_point):
    pass
