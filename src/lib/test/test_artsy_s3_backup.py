import pytz
import re

from datetime import datetime
from dateutil.parser import parse as parsedatetime

from lib.test.fixtures.artsy_s3_backup import backup_obj
from lib.test.fixtures.s3_interface import (
  mock_s3_interface, # indirect usage
  mock_s3_list_objects_result # indirect usage
)

def describe_artsy_s3_backup():

  def describe_instantiation():
    def it_instantiates(backup_obj):
      assert backup_obj.s3_bucket == 'foobucket'

  def describe_backup_id_to_s3_key():
    def it_returns_key(backup_obj):
      id = 'foo'
      key = backup_obj._backup_id_to_s3_key(id)
      assert key == 'fooprefix/fooapp/fooenv/foo.tar.gz'

  def describe_backup_id():
    def it_returns_an_id(backup_obj):
      id = backup_obj._backup_id()
      # sample id: 2023-07-01_23:30:25.608581+00:00
      regex = re.compile("\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}:\d{2}")
      assert re.match(regex, id) is not None

  def describe_is_backup():
    def it_returns_true_if_key_has_suffix(backup_obj):
      assert backup_obj._is_backup('foo.tar.gz') == True
    def it_returns_false_if_key_does_not_have_suffix(backup_obj):
      assert backup_obj._is_backup('foo.gz') == False

  def describe_s3_key_to_backup_id():
    def it_returns_backup_id(backup_obj):
      key = 'fooprefix/fooapp/fooenv/2023-07-01_23:30:25.608581+00:00.tar.gz'
      expected_id = '2023-07-01_23:30:25.608581+00:00'
      assert backup_obj._s3_key_to_backup_id(key) == expected_id

  def describe_backup():
    def it_calls_s3_interface_put_file(backup_obj, mocker):
      mocker.patch.object(backup_obj, '_backup_id_to_s3_key', return_value='fookey')
      spy = mocker.spy(backup_obj._s3_interface, 'put_file')
      file = 'path/to/file'
      backup_obj.backup(file)
      spy.assert_has_calls([mocker.call(file, 'foobucket', 'fookey')])

  def describe_backups():
    def it_returns_backups(backup_obj):
      assert backup_obj.backups() == ['2023-07-01_00:22:49.920207+00:00']

  def describe_created_at():
    def it_returns_timestamp(backup_obj):
      id = '2023-07-01_00:22:49.920207+00:00'
      assert backup_obj.created_at(id) == '2023-07-01 00:22:49.920207+00:00'

  def describe_delete():
    def it_calls_s3_interface_delete_object(backup_obj, mocker):
      id = '2023-07-01_00:22:49.920207+00:00'
      spy = mocker.spy(backup_obj._s3_interface, 'delete_object')
      backup_obj.delete(id)
      spy.assert_has_calls([
        mocker.call(
          'foobucket',
          'fooprefix/fooapp/fooenv/2023-07-01_00:22:49.920207+00:00.tar.gz'
        )
      ])

  def describe_old_backups():
    def it_returns_old_backups(backup_obj):
      ids = backup_obj.backups()
      assert len(ids) == 1
      timestamp = backup_obj.created_at(ids[0])
      date_obj = parsedatetime(timestamp)
      now = datetime.utcnow()
      now_utc = now.replace(tzinfo=pytz.utc)
      delta = now_utc - date_obj
      # the backup in the fixture is dated 'days' ago
      days = delta.days
      # so it's more than days-1 days ago
      old = backup_obj.old_backups(days-1)
      assert old == ['2023-07-01_00:22:49.920207+00:00']
      # but more recent than days+1 days ago
      old = backup_obj.old_backups(days+1)
      assert old == []
