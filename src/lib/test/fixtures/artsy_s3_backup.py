import pytest

from lib.artsy_s3_backup import ArtsyS3Backup
from lib.test.fixtures.s3_interface import mock_s3_interface

@pytest.fixture
def backup_obj(mock_s3_interface):
  obj = ArtsyS3Backup(
    'foobucket',
    'fooprefix',
    'fooapp',
    'fooenv',
    'tar.gz',
    mock_s3_interface
  )
  return obj
