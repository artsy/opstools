import pytest


@pytest.fixture
def mock_artsy_s3_backup_class1():
  class MockArtsyS3Backup():
    def __init__(self, *args):
      init_spy(*args)
    def backup(self, *args):
      backup_spy(*args)
  return MockArtsyS3Backup

def init_spy(a,b,c,d,e):
  pass

def backup_spy(a):
  pass

@pytest.fixture
def mock_artsy_s3_backup_class2():
  class MockArtsyS3Backup():
    def __init__(self, *args):
      pass
    def backup(self, *args):
      raise Exception
  return MockArtsyS3Backup
