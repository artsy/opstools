import json
import pytest

import lib.kctl

from lib.kctl import \
  check_output, \
  Kctl, \
  kctl_client

from lib.test.fixtures.kctl import \
  mock_kubectl_get_namespaces_json_object, \
  mock_kubectl_get_namespaces_json_string, \
  mock_kubectl_get_pods_json_object, \
  mock_kubectl_get_pods_json_string

def describe_kctl():
  def describe_no_context():
    def describe_instantiation():
      def it_does_not_instantiate_when_no_context_param():
        with pytest.raises(TypeError):
          kctl = Kctl()
      def it_instantiates_when_context_none():
        kctl = Kctl(None)
    def describe_run():
      def describe_no_timeout_supplied():
        def it_calls_check_output_with_correct_params(mocker):
          kctl = Kctl(None)
          mocker.patch('lib.kctl.check_output')
          check_output_spy = mocker.spy(lib.kctl, 'check_output')
          kctl._run('get pods')
          check_output_spy.assert_has_calls([
            mocker.call('kubectl get pods', timeout=30, shell=True)
          ])
      def describe_timeout_supplied():
        def it_calls_check_output_with_correct_params(mocker):
          kctl = Kctl(None)
          mocker.patch('lib.kctl.check_output')
          check_output_spy = mocker.spy(lib.kctl, 'check_output')
          kctl._run('get pods', timeout=90)
          check_output_spy.assert_has_calls([
            mocker.call('kubectl get pods', timeout=90, shell=True)
          ])
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
        check_output_spy.assert_has_calls([
          mocker.call(
            'kubectl --context staging get pods', timeout=30, shell=True
          )
        ])
    def describe_get_namespaces():
      def it_gets_namespaces(
        mocker,
        mock_kubectl_get_namespaces_json_object,
        mock_kubectl_get_namespaces_json_string
      ):
        mocker.patch(
          'lib.kctl.Kctl._run',
          return_value=mock_kubectl_get_namespaces_json_string
        )
        data = kctl.get_namespaces()
        assert data == mock_kubectl_get_namespaces_json_object['items']
    def describe_delete_namespace():
      def it_calls_run_with_correct_params(mocker):
        mocker.patch('lib.kctl.Kctl._run')
        kctl_run_spy = mocker.spy(lib.kctl.Kctl, '_run')
        kctl.delete_namespace('foo')
        kctl_run_spy.assert_has_calls([mocker.call('delete namespace foo')])
    def describe_delete_pod():
      def it_calls_run_with_correct_params(mocker):
        mocker.patch('lib.kctl.Kctl._run')
        kctl_run_spy = mocker.spy(lib.kctl.Kctl, '_run')
        kctl.delete_pod('foo', 'bar')
        kctl_run_spy.assert_has_calls(
          [mocker.call('delete pod bar -n foo', timeout=90)]
        )
    def describe_get_pods():
      def it_gets_pods(
          mocker,
          mock_kubectl_get_pods_json_object,
          mock_kubectl_get_pods_json_string
        ):
        mocker.patch(
          'lib.kctl.Kctl._run',
          return_value=mock_kubectl_get_pods_json_string
        )
        kctl_run_spy = mocker.spy(lib.kctl.Kctl, '_run')
        data = kctl.get_pods('foo')
        kctl_run_spy.assert_has_calls([mocker.call('get pods -n foo -o json')])
        assert data == mock_kubectl_get_pods_json_object['items']

def describe_kctl_client():
  def describe_empty_context():
    def it_instantiates_with_none(mocker):
      mocker.patch(
        'lib.kctl.Kctl.__init__'
      ).side_effect = [None]
      kctl_init_spy = mocker.spy(
        lib.kctl.Kctl, '__init__'
      )
      kctl = kctl_client('')
      assert isinstance(kctl, Kctl)
      kctl_init_spy.call_count == 1
      kctl_init_spy.assert_has_calls([mocker.call(None)])
  def describe_context():
    def it_instantiates_with_context(mocker):
      mocker.patch(
        'lib.kctl.Kctl.__init__'
      ).side_effect = [None]
      kctl_init_spy = mocker.spy(
        lib.kctl.Kctl, '__init__'
      )
      kctl = kctl_client('foo')
      assert isinstance(kctl, Kctl)
      kctl_init_spy.call_count == 1
      kctl_init_spy.assert_has_calls([mocker.call('foo')])
