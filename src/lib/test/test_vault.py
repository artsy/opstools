import pytest

import lib.vault

from lib.vault import Vault
from lib.test.fixtures.vault import (
  mock_exception_function,
  mock_hvac_client_class
)

def describe_vault():
  def describe_init():
    def it_inits(mocker):
      mocker.patch('lib.vault.boto3')
      mocker.patch('lib.vault.hvac.Client')
      obj = Vault('fooaddr', 'token', 'footoken', None, 'foomountpoint', 'foopath', 'foosanitizer')
      assert obj._client is lib.vault.hvac.Client()
      assert obj._mount_point == 'foomountpoint'
      assert obj._path == 'foopath'
      assert obj._sanitizer == 'foosanitizer'
      assert obj._client.token == 'footoken'

  def describe_login():
    def it_calls_iam_login_when_auth_method_is_iam(mocker):
      mocker.patch('lib.vault.boto3')
      mocker.patch('lib.vault.hvac.Client')
      obj = Vault('fooaddr', 'iam', role='foorole')
      spy = mocker.spy(obj, '_iam_login')
      obj._login('iam', role='foorole')
      spy.assert_has_calls([
        mocker.call(
          'foorole'
        )
      ])
    def it_sets_token_when_auth_method_is_token(mocker):
      mocker.patch('lib.vault.boto3')
      mocker.patch('lib.vault.hvac.Client')
      obj = Vault('fooaddr', 'token')
      spy = mocker.spy(obj, '_login')
      obj._login('token', token='footoken')
      assert obj._client.token == 'footoken'
    def it_raises_when_unsupported_auth_method(mocker):
      mocker.patch('lib.vault.boto3')
      mocker.patch('lib.vault.hvac.Client')
      obj = Vault('fooaddr', 'token')
      with pytest.raises(Exception):
        obj._login('fooauthmethod')

  def describe_iam_login():
    def it_raises_when_role_is_none(mocker):
      mocker.patch('lib.vault.boto3')
      mocker.patch('lib.vault.hvac.Client')
      obj = Vault('fooaddr', 'iam', role='foorole')
      with pytest.raises(Exception):
        obj._iam_login(None)
    def it_does_the_right_things_when_role_is_specified(mocker):
      mock_boto3 = mocker.patch('lib.vault.boto3')
      mocker.patch('lib.vault.hvac.Client')
      obj = Vault('fooaddr', 'iam', role='foorole')
      spy = mocker.spy(obj._client.auth.aws, 'iam_login')
      obj._iam_login('foorole')
      spy.assert_has_calls([
        mocker.call(
          lib.vault.boto3.Session().get_credentials().access_key,
          lib.vault.boto3.Session().get_credentials().secret_key,
          lib.vault.boto3.Session().get_credentials().token,
          role='foorole'
        )
      ])

  def describe_get():
    def describe_key_does_not_exist():
      def it_raises(mocker, mock_hvac_client_class):
        mocker.patch('lib.vault.boto3')
        mocker.patch('lib.vault.hvac.Client').side_effect = mock_hvac_client_class
        obj = Vault('fooaddr', 'token', 'footoken', None, 'foomountpoint', 'foopath', 'foosanitizer')
        with pytest.raises(KeyError):
          obj.get('barkey')
    def describe_key_exists():
      def it_gets(mocker):
        mocker.patch('lib.vault.boto3')
        mocker.patch('lib.vault.hvac.Client')
        obj = Vault('fooaddr', 'token', 'footoken', None, 'foomountpoint', 'foopath', 'foosanitizer')
        spy = mocker.spy(obj._client.secrets.kv, 'read_secret_version')
        assert obj.get('fookey') == lib.vault.hvac.Client().secrets.kv.read_secret_version()['data']['data']['key']
        spy.assert_has_calls([
          mocker.call(
            path='foopathfookey',
            mount_point='foomountpoint'
          )
        ])

  def describe_get_set():
    def describe_no_value():
      def it_sets(mocker, mock_exception_function):
        mocker.patch('lib.vault.boto3')
        mocker.patch('lib.vault.hvac.Client')
        obj = Vault('fooaddr', 'token', 'footoken', None, 'foomountpoint', 'foopath', 'foosanitizer')
        mocker.patch.object(obj, 'get').side_effect = mock_exception_function
        mocker.patch.object(obj, 'set')
        spy = mocker.spy(obj, 'set')
        obj.get_set('fookey', 'foovalue')
        spy.assert_has_calls([
          mocker.call('fookey', 'foovalue', False)
        ])
    def describe_different_value():
      def it_sets(mocker):
        mocker.patch('lib.vault.boto3')
        mocker.patch('lib.vault.hvac.Client')
        def foosanitizer(value):
          pass
        obj = Vault('fooaddr', 'token', 'footoken', None, 'foomountpoint', 'foopath', foosanitizer)
        mocker.patch.object(obj, 'get', return_value='barvalue')
        mocker.patch.object(obj, 'set')
        spy = mocker.spy(obj, 'set')
        obj.get_set('fookey', 'foovalue')
        spy.assert_has_calls([
          mocker.call('fookey', 'foovalue', False)
        ])
    def describe_same_value():
      def it_skips(mocker):
        mocker.patch('lib.vault.boto3')
        mocker.patch('lib.vault.hvac.Client')
        def foosanitizer(value):
          return value
        obj = Vault('fooaddr', 'token', 'footoken', None, 'foomountpoint', 'foopath', foosanitizer)
        mocker.patch.object(obj, 'get', return_value='foovalue')
        mocker.patch.object(obj, 'set')
        spy = mocker.spy(obj, 'set')
        obj.get_set('fookey', 'foovalue')
        assert spy.call_count == 0

  def describe_list():
    def it_lists(mocker):
      mocker.patch('lib.vault.boto3')
      mocker.patch('lib.vault.hvac.Client')
      obj = Vault('fooaddr', 'token', 'footoken', None, 'foomountpoint', 'foopath', 'foosanitizer')
      spy = mocker.spy(obj._client.secrets.kv.v2, 'list_secrets')
      assert obj.list() == lib.vault.hvac.Client().secrets.kv.v2.list_secrets()
      spy.assert_has_calls([
        mocker.call(
          path='foopath',
          mount_point='foomountpoint'
        )
      ])

  def describe_set():
    def it_sets(mocker):
      mocker.patch('lib.vault.boto3')
      mocker.patch('lib.vault.hvac.Client')
      def foosanitizer(value):
        return value
      obj = Vault('fooaddr', 'token', 'footoken', None, 'foomountpoint', 'foopath', foosanitizer)
      spy = mocker.spy(obj._client.secrets.kv.v2, 'create_or_update_secret')
      obj.set('fookey', 'foovalue')
      spy.assert_has_calls([
        mocker.call(
          path='foopathfookey',
          secret={'fookey': 'foovalue'},
          mount_point='foomountpoint'
        )
      ])
    def it_does_not_set_when_dry_run(mocker):
      mocker.patch('lib.vault.boto3')
      mocker.patch('lib.vault.hvac.Client')
      def foosanitizer(value):
        return value
      obj = Vault('fooaddr', 'token', 'footoken', None, 'foomountpoint', 'foopath', foosanitizer)
      spy = mocker.spy(obj._client.secrets.kv.v2, 'create_or_update_secret')
      obj.set('fookey', 'foovalue', True)
      assert spy.call_count == 0

  def describe_take_snapshot():
    def it_does_the_right_things(mocker):
      mocker.patch('lib.vault.boto3')
      mocker.patch('lib.vault.hvac.Client')
      mocker.patch('lib.vault.write_file')
      obj = Vault('fooaddr', 'iam', role='foorole')
      spy = mocker.spy(lib.vault, 'write_file')
      obj.take_snapshot('foofile')
      spy.assert_has_calls([
        mocker.call(
          'foofile',
          obj._client.sys.take_raft_snapshot().content,
          data_format='binary'
        )
      ])
