import pytest

import lib.vault

from lib.vault import Vault
from lib.test.fixtures.vault import (
  mock_exception_function,
  mock_hvac_client_class
)

def describe_vault():
  def describe_init():
    def it_inits(mocker, mock_hvac_client_class):
      mocker.patch('lib.vault.hvac.Client').side_effect = mock_hvac_client_class
      def foosanitizer():
        pass
      obj = Vault('fooaddr', 'foomountpoint', 'foopath', 'footoken', foosanitizer)
      assert isinstance(obj._client, mock_hvac_client_class)
      assert obj._mount_point == 'foomountpoint'
      assert obj._path == 'foopath'
      assert obj._sanitizer == foosanitizer

  def describe_get():
    def describe_key_does_not_exist():
      def it_raises(mocker, mock_hvac_client_class):
        mocker.patch('lib.vault.hvac.Client').side_effect = mock_hvac_client_class
        def foosanitizer():
          pass
        obj = Vault('fooaddr', 'foomountpoint', 'foopath', 'footoken', foosanitizer)
        spy = mocker.spy(obj._client.secrets.kv, 'read_secret_version')
        with pytest.raises(Exception):
          obj.get('barkey')
    def describe_key_exists():
      def it_gets(mocker, mock_hvac_client_class):
        mocker.patch('lib.vault.hvac.Client').side_effect = mock_hvac_client_class
        def foosanitizer():
          pass
        obj = Vault('fooaddr', 'foomountpoint', 'foopath', 'footoken', foosanitizer)
        spy = mocker.spy(obj._client.secrets.kv, 'read_secret_version')
        assert obj.get('fookey') == 'foovalue'
        spy.assert_has_calls([
          mocker.call(
            path='foopathfookey',
            mount_point='foomountpoint'
          )
        ])

  def describe_get_set():
    def describe_no_value():
      def it_sets(mocker, mock_hvac_client_class, mock_exception_function):
        mocker.patch('lib.vault.hvac.Client').side_effect = mock_hvac_client_class
        def foosanitizer():
          pass
        obj = Vault('fooaddr', 'foomountpoint', 'foopath', 'footoken', foosanitizer)
        mocker.patch.object(obj, 'get').side_effect = mock_exception_function
        mocker.patch.object(obj, 'set')
        spy = mocker.spy(obj, 'set')
        obj.get_set('fookey', 'foovalue')
        spy.assert_has_calls([
          mocker.call('fookey', 'foovalue', False)
        ])
    def describe_different_value():
      def it_sets(mocker, mock_hvac_client_class):
        mocker.patch('lib.vault.hvac.Client').side_effect = mock_hvac_client_class
        def foosanitizer(value):
          pass
        obj = Vault('fooaddr', 'foomountpoint', 'foopath', 'footoken', foosanitizer)
        mocker.patch.object(obj, 'get', return_value='barvalue')
        mocker.patch.object(obj, 'set')
        spy = mocker.spy(obj, 'set')
        obj.get_set('fookey', 'foovalue')
        spy.assert_has_calls([
          mocker.call('fookey', 'foovalue', False)
        ])
    def describe_same_value():
      def it_skips(mocker, mock_hvac_client_class):
        mocker.patch('lib.vault.hvac.Client').side_effect = mock_hvac_client_class
        def foosanitizer(value):
          return value
        obj = Vault('fooaddr', 'foomountpoint', 'foopath', 'footoken', foosanitizer)
        mocker.patch.object(obj, 'get', return_value='foovalue')
        mocker.patch.object(obj, 'set')
        spy = mocker.spy(obj, 'set')
        obj.get_set('fookey', 'foovalue')
        assert spy.call_count == 0

  def describe_list():
    def it_lists(mocker, mock_hvac_client_class):
      mocker.patch('lib.vault.hvac.Client').side_effect = mock_hvac_client_class
      def foosanitizer():
        pass
      obj = Vault('fooaddr', 'foomountpoint', 'foopath', 'footoken', foosanitizer)
      spy = mocker.spy(obj._client.secrets.kv.v2, 'list_secrets')
      assert obj.list() == ['fookey', 'barkey']
      spy.assert_has_calls([
        mocker.call(
          path='foopath',
          mount_point='foomountpoint'
        )
      ])

  def describe_set():
    def it_sets(mocker, mock_hvac_client_class):
      mocker.patch('lib.vault.hvac.Client').side_effect = mock_hvac_client_class
      def foosanitizer(value):
        return value
      obj = Vault('fooaddr', 'foomountpoint', 'foopath', 'footoken', foosanitizer)
      spy = mocker.spy(obj._client.secrets.kv.v2, 'create_or_update_secret')
      obj.set('fookey', 'foovalue')
      spy.assert_has_calls([
        mocker.call(
          path='foopathfookey',
          secret={'fookey': 'foovalue'},
          mount_point='foomountpoint'
        )
      ])
    def it_does_not_set_when_dry_run(mocker, mock_hvac_client_class):
      mocker.patch('lib.vault.hvac.Client').side_effect = mock_hvac_client_class
      def foosanitizer(value):
        return value
      obj = Vault('fooaddr', 'foomountpoint', 'foopath', 'footoken', foosanitizer)
      spy = mocker.spy(obj._client.secrets.kv.v2, 'create_or_update_secret')
      obj.set('fookey', 'foovalue', True)
      assert spy.call_count == 0
