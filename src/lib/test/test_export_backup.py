import os
import pytest

import lib.export_backup

from lib.export_backup import (
  backup_to_s3,
  setup_local_export_dir,
  write_file,
  write_binary_file,
  write_text_file
)
from lib.test.fixtures.export_backup import (
  backup_spy,
  mock_artsy_s3_backup_class1,
  mock_artsy_s3_backup_class2
)


def describe_backup_to_s3():
  def it_raises_when_not_artsy_bucket(mocker):
    mocker.patch('lib.export_backup.is_artsy_s3_bucket').return_value = False
    with pytest.raises(Exception):
      backup_to_s3()
  def it_does_the_right_things(mocker, mock_artsy_s3_backup_class1):
    mocker.patch('lib.export_backup.ArtsyS3Backup').side_effect = mock_artsy_s3_backup_class1
    mocker.patch('lib.export_backup.is_artsy_s3_bucket').return_value = True
    mocker.patch('lib.export_backup.shutil.rmtree')
    init_spy = mocker.spy(lib.test.fixtures.export_backup, 'init_spy')
    backup_spy = mocker.spy(lib.test.fixtures.export_backup, 'backup_spy')
    rmtree_spy = mocker.spy(lib.export_backup.shutil, 'rmtree')
    backup_to_s3('foobucket', 'fooprefix', 'fooservice', 'fooenv', 'foosuffix', 'foofile', 'foodir')
    init_spy.assert_has_calls([
      mocker.call('foobucket', 'fooprefix', 'fooservice', 'fooenv', 'foosuffix')
    ])
    backup_spy.assert_has_calls([
      mocker.call('foofile')
    ])
    rmtree_spy.assert_has_calls([
      mocker.call('foodir')
    ])
  def it_cleans_up_even_when_exception(mocker, mock_artsy_s3_backup_class2):
    mocker.patch('lib.export_backup.ArtsyS3Backup').side_effect = mock_artsy_s3_backup_class2
    mocker.patch('lib.export_backup.is_artsy_s3_bucket').return_value = True
    mocker.patch('lib.export_backup.shutil.rmtree')
    rmtree_spy = mocker.spy(lib.export_backup.shutil, 'rmtree')
    with pytest.raises(Exception):
      backup_to_s3('foobucket', 'fooprefix', 'fooservice', 'fooenv', 'foosuffix', 'foofile', 'foodir')
    rmtree_spy.assert_has_calls([
      mocker.call('foodir')
    ])

def describe_setup_local_export_dir():
  def it_returns_correct_dir_file_path(mocker):
    mocker.patch('lib.export_backup.mkpath')
    dir_path, file_path = setup_local_export_dir('foodir', 'fooenv', 'foohost', 'foosuffix')
    assert dir_path == 'foodir/fooenv'
    assert file_path == 'foodir/fooenv/foohost.foosuffix'

def describe_write_file():
  def it_calls_write_text_file_when_format_is_text(mocker):
    mocker.patch('lib.export_backup.write_text_file')
    mocker.patch('lib.export_backup.write_binary_file')
    text_spy = mocker.spy(lib.export_backup, 'write_text_file')
    binary_spy = mocker.spy(lib.export_backup, 'write_binary_file')
    write_file('foofile', 'foodata', 'text')
    text_spy.assert_has_calls([
      mocker.call('foofile', 'foodata', None, int(0o600), True)
    ])
    assert not binary_spy.called
  def it_calls_write_binary_file_when_format_is_binary(mocker):
    mocker.patch('lib.export_backup.write_text_file')
    mocker.patch('lib.export_backup.write_binary_file')
    text_spy = mocker.spy(lib.export_backup, 'write_text_file')
    binary_spy = mocker.spy(lib.export_backup, 'write_binary_file')
    write_file('foofile', 'foodata', 'binary')
    binary_spy.assert_has_calls([
      mocker.call('foofile', 'foodata', int(0o600), True)
    ])
    assert not text_spy.called
  def it_raises_when_format_unsupported(mocker):
    mocker.patch('lib.export_backup.write_text_file')
    mocker.patch('lib.export_backup.write_binary_file')
    with pytest.raises(Exception):
      write_file('foofile', 'foodata', 'fooformat')

def describe_write_text_file():
  def it_creates_file_with_default_permissions(tmp_path):
    file_path = os.path.join(tmp_path, 'foo.txt')
    write_file(file_path, 'foo data')
    assert os.stat(file_path).st_mode == int(0o100600)
    with open(file_path, 'r') as f:
      assert f.readline().strip() == 'foo data'
  def it_creates_file_with_custom_permissions(tmp_path):
    file_path = os.path.join(tmp_path, 'foo.txt')
    write_file(file_path, 'foo data', mode=0o755)
    assert os.stat(file_path).st_mode == int(0o100755)
  def it_writes_heading(tmp_path):
    file_path = os.path.join(tmp_path, 'foo.txt')
    write_file(file_path, 'foo data', heading='foo heading\n')
    with open(file_path, 'r') as f:
      assert f.readline().strip() == 'foo heading'
  def it_balks_when_file_exists(tmp_path):
    file_path = os.path.join(tmp_path, 'foo.txt')
    write_file(file_path, 'foo data')
    write_file(file_path, 'foo data')
    with pytest.raises(FileExistsError):
      write_file(file_path, 'foo data', exist_ok=False)

def describe_write_binary_file():
  def it_creates_file_with_default_permissions(tmp_path):
    file_path = os.path.join(tmp_path, 'foo.bin')
    write_binary_file(file_path, b'foo data')
    assert os.stat(file_path).st_mode == int(0o100600)
    with open(file_path, 'rb') as f:
      assert f.readline() == b'foo data'
  def it_creates_file_with_custom_permissions(tmp_path):
    file_path = os.path.join(tmp_path, 'foo.bin')
    write_binary_file(file_path, b'foo data', mode=0o755)
    assert os.stat(file_path).st_mode == int(0o100755)
  def it_balks_when_file_exists(tmp_path):
    file_path = os.path.join(tmp_path, 'foo.bin')
    write_file(file_path, 'foo data')
    write_file(file_path, 'foo data')
    with pytest.raises(FileExistsError):
      write_file(file_path, 'foo data', exist_ok=False)
