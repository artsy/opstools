import json
import pytest

import lib.kctl

from lib.kctl import \
  check_output, \
  Kctl

def describe_kctl():
  def describe_no_context():
    def describe_instantiation():
      def it_does_not_instantiate_when_no_context_param():
        with pytest.raises(TypeError):
          kctl = Kctl()
      def it_instantiates_when_context_none():
        kctl = Kctl(None)
    def describe_run():
      def it_calls_check_output_with_correct_params(mocker):
        kctl = Kctl(None)
        mocker.patch('lib.kctl.check_output')
        check_output_spy = mocker.spy(lib.kctl, 'check_output')
        kctl._run('get pods')
        check_output_spy.assert_has_calls([mocker.call('kubectl get pods', timeout=30, shell=True)])
  def describe_with_context():
    kctl = Kctl('staging')
    def describe_instantiation():
      def it_instantiates_with_context_param():
        assert kctl._context == 'staging'
    def describe_run():
      def it_calls_check_output_with_correct_params(mocker):
        mocker.patch('lib.kctl.check_output')
        check_output_spy = mocker.spy(lib.kctl, 'check_output')
        kctl._run('get pods')
        check_output_spy.assert_has_calls([mocker.call('kubectl --context staging get pods', timeout=30, shell=True)])
    def describe_get_namespaces():
      def it_gets_namespaces(mocker):
        obj = {
          'items': [
            'namespace1',
            'namespace2'
          ]
        }
        mock_get_namespaces_output = json.dumps(obj)
        mocker.patch('lib.kctl.Kctl._run', return_value=mock_get_namespaces_output)
        data = kctl.get_namespaces()
        assert data == obj['items']
    def describe_delete_namespace():
      def it_calls_run_with_correct_params(mocker):
        mocker.patch('lib.kctl.Kctl._run')
        kctl_run_spy = mocker.spy(lib.kctl.Kctl, '_run')
        kctl.delete_namespace('foo')
        kctl_run_spy.assert_has_calls([mocker.call('delete namespace foo')])
