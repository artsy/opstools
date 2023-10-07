import json
import pytest

from subprocess import CompletedProcess

import lib.kctl

from lib.kctl import (
  subprocess_run,
  Kctl,
)

from lib.test.fixtures.kctl import (
  mock_kubectl_get_configmaps_json_object,
  mock_kubectl_get_configmaps_json_string,
  mock_kubectl_get_namespaces_json_object,
  mock_kubectl_get_namespaces_json_string,
  mock_kubectl_get_pods_json_object,
  mock_kubectl_get_pods_json_string,
  mock_kubectl_get_jobs_json_object,
  mock_kubectl_get_jobs_json_string
)

def describe_kctl():
  def describe_instantiation():
    def it_instantiates():
      kctl = Kctl(True, 'staging')
      assert kctl._context == 'staging'
      assert kctl._in_cluster == True

  def describe_in_cluster():
    def describe_run():
      def describe_sucess_not_expected():
        def it_calls_subprocess_run_with_correct_params(mocker):
          kctl = Kctl(True, 'staging')
          mocker.patch(
            'lib.kctl.subprocess_run',
            return_value=CompletedProcess('foo', 0)
          )
          subprocess_run_spy = mocker.spy(lib.kctl, 'subprocess_run')
          resp = kctl._run('get pods')
          subprocess_run_spy.assert_has_calls([
            mocker.call(
              'kubectl get pods',
              capture_output=True,
              shell=True,
              text=True,
              timeout=30,
            )
          ])
          assert resp.returncode == 0
        def it_calls_run_with_custom_timeout(mocker):
          kctl = Kctl(True, 'staging')
          mocker.patch(
            'lib.kctl.subprocess_run',
            return_value=CompletedProcess('foo', 0)
          )
          subprocess_run_spy = mocker.spy(lib.kctl, 'subprocess_run')
          resp = kctl._run('get pods', timeout=90)
          subprocess_run_spy.assert_has_calls([
            mocker.call(
              'kubectl get pods',
              capture_output=True,
              shell=True,
              text=True,
              timeout=90,
            )
          ])
          assert resp.returncode == 0
        def it_does_not_raise_exception_when_command_fails(mocker):
          kctl = Kctl(True, 'staging')
          mocker.patch(
            'lib.kctl.subprocess_run',
            return_value=CompletedProcess('foo', 1)
          )
          resp = kctl._run('get pods')
          assert resp.returncode == 1
      def describe_sucess_expected():
        def it_raises_exception_when_command_fails(mocker):
          kctl = Kctl(True, 'staging')
          mocker.patch(
            'lib.kctl.subprocess_run',
            return_value=CompletedProcess('foo', 1)
          )
          with pytest.raises(Exception):
            resp = kctl._run('get pods', expect_success=True)
            assert resp.returncode == 1

  def describe_outside_cluster():
    def describe_run():
      def it_calls_run_with_correct_params(mocker):
        kctl = Kctl(False, 'staging')
        mocker.patch(
          'lib.kctl.subprocess_run',
          return_value=CompletedProcess('foo', 0)
        )
        subprocess_run_spy = mocker.spy(lib.kctl, 'subprocess_run')
        resp = kctl._run('get pods')
        subprocess_run_spy.assert_has_calls([
          mocker.call(
            'kubectl --context staging get pods',
            capture_output=True,
            shell=True,
            text=True,
            timeout=30,
          )
        ])
        assert resp.returncode == 0

    def describe_annotate():
      def it_calls_run_with_correct_params(mocker):
        kctl = Kctl(False, 'staging')
        mocker.patch('lib.kctl.Kctl._run')
        kctl_run_spy = mocker.spy(lib.kctl.Kctl, '_run')
        kctl.annotate('footype', 'fooname', 'fooannotation')
        kctl_run_spy.assert_has_calls([
          mocker.call(
            '-n default annotate footype fooname fooannotation --overwrite',
            expect_success=True
          )
        ])

    def describe_delete_job():
      def it_calls_delete_namespaced_object_with_correct_params(mocker):
        kctl = Kctl(False, 'staging')
        mocker.patch('lib.kctl.Kctl.delete_namespaced_object')
        dno_spy= mocker.spy(lib.kctl.Kctl, 'delete_namespaced_object')
        kctl.delete_job('foojob')
        dno_spy.assert_has_calls(
          [mocker.call('job', 'foojob', 'default')]
        )

    def describe_delete_namespace():
      def it_calls_run_with_correct_params(mocker):
        kctl = Kctl(False, 'staging')
        mocker.patch('lib.kctl.Kctl._run')
        kctl_run_spy = mocker.spy(lib.kctl.Kctl, '_run')
        kctl.delete_namespace('foo')
        kctl_run_spy.assert_has_calls([
          mocker.call('delete namespace foo', timeout=90, expect_success=True)
        ])

    def describe_delete_namespaced_object():
      def it_calls_run_with_correct_params(mocker):
        kctl = Kctl(False, 'staging')
        mocker.patch(
          'lib.kctl.Kctl._run',
          return_value=CompletedProcess('foo', 0)
        )
        kctl_run_spy = mocker.spy(lib.kctl.Kctl, '_run')
        kctl.delete_namespaced_object('job', 'foojob', 'default')
        kctl_run_spy.assert_has_calls([
          mocker.call('-n default delete job foojob', timeout=90)
        ])
      def it_ignores_not_found_errors(mocker):
        kctl = Kctl(False, 'staging')
        mocker.patch(
          'lib.kctl.Kctl._run',
          return_value=CompletedProcess('foo', 1, stderr='not found')
        )
        kctl.delete_namespaced_object('job', 'foojob', 'default')
      def it_raises_exception_for_other_errors(mocker):
        kctl = Kctl(False, 'staging')
        mocker.patch(
          'lib.kctl.Kctl._run',
          return_value=CompletedProcess('foo', 1, stderr='other error')
        )
        with pytest.raises(Exception):
          kctl.delete_namespaced_object('job', 'foojob', 'default')

    def describe_delete_pod():
      def it_calls_delete_namespaced_object_with_correct_params(mocker):
        kctl = Kctl(False, 'staging')
        mocker.patch('lib.kctl.Kctl.delete_namespaced_object')
        dno_spy= mocker.spy(lib.kctl.Kctl, 'delete_namespaced_object')
        kctl.delete_pod('foopod')
        dno_spy.assert_has_calls(
          [mocker.call('pod', 'foopod', 'default')]
        )

    def describe_get_jobs():
      def it_gets_jobs(
          mocker,
          mock_kubectl_get_jobs_json_object,
          mock_kubectl_get_jobs_json_string
        ):
        kctl = Kctl(False, 'staging')
        mocker.patch(
          'lib.kctl.Kctl.get_namespaced_object',
          return_value=mock_kubectl_get_jobs_json_string
        )
        gno_spy = mocker.spy(lib.kctl.Kctl, 'get_namespaced_object')
        data = kctl.get_jobs('foonamespace')
        gno_spy.assert_has_calls([
          mocker.call('jobs', 'json', 'foonamespace')
        ])
        assert data == mock_kubectl_get_jobs_json_object['items']

    def describe_get_namespaced_object():
      def describe_when_no_resource_name():
        def it_calls_run_with_correct_params(mocker):
          kctl = Kctl(False, 'staging')
          mocker.patch(
            'lib.kctl.Kctl._run',
            return_value=CompletedProcess('foo', 0, stdout='foooutput')
          )
          kctl_run_spy = mocker.spy(lib.kctl.Kctl, '_run')
          output = kctl.get_namespaced_object('jobs', 'json', 'default')
          kctl_run_spy.assert_has_calls([
            mocker.call('-n default get jobs -o json', expect_success=True)
          ])
          assert output == 'foooutput'
      def describe_when_resource_name():
        def it_calls_run_with_correct_params(mocker):
          kctl = Kctl(False, 'staging')
          mocker.patch(
            'lib.kctl.Kctl._run',
            return_value=CompletedProcess('foo', 0, stdout='foooutput')
          )
          kctl_run_spy = mocker.spy(lib.kctl.Kctl, '_run')
          output = kctl.get_namespaced_object('jobs', 'json', 'default', 'fooresource')
          kctl_run_spy.assert_has_calls([
            mocker.call('-n default get jobs fooresource -o json', expect_success=True)
          ])
          assert output == 'foooutput'

    def describe_get_namespaces():
      def it_gets_namespaces(
        mocker,
        mock_kubectl_get_namespaces_json_object,
        mock_kubectl_get_namespaces_json_string
      ):
        kctl = Kctl(False, 'staging')
        mocker.patch(
          'lib.kctl.Kctl._run',
          return_value=CompletedProcess(
            'foo', 0, stdout=mock_kubectl_get_namespaces_json_string
          )
        )
        data = kctl.get_namespaces()
        assert data == mock_kubectl_get_namespaces_json_object['items']

    def describe_get_pods():
      def it_gets_pods(
          mocker,
          mock_kubectl_get_pods_json_object,
          mock_kubectl_get_pods_json_string
        ):
        kctl = Kctl(False, 'staging')
        mocker.patch(
          'lib.kctl.Kctl.get_namespaced_object',
          return_value=mock_kubectl_get_pods_json_string
        )
        gno_spy = mocker.spy(lib.kctl.Kctl, 'get_namespaced_object')
        data = kctl.get_pods('foonamespace')
        gno_spy.assert_has_calls([
          mocker.call('pods', 'json', 'foonamespace')
        ])
        assert data == mock_kubectl_get_pods_json_object['items']

    def describe_get_configmap():
      def it_gets_the_named_configmap(mocker):
        kctl = Kctl(False, 'staging')
        mock_configmap = {'foo': 'bar'}
        mocker.patch(
          'lib.kctl.Kctl.get_namespaced_object',
          return_value=json.dumps(mock_configmap)
        )
        gno_spy = mocker.spy(lib.kctl.Kctl, 'get_namespaced_object')
        data = kctl.get_configmap('fooconfigmap', 'foonamespace')
        gno_spy.assert_has_calls([
          mocker.call('configmaps', 'json', 'foonamespace', 'fooconfigmap')
        ])
        assert data == mock_configmap

    def describe_get_configmaps():
      def it_gets_configmaps(
          mocker,
          mock_kubectl_get_configmaps_json_object,
          mock_kubectl_get_configmaps_json_string
        ):
        kctl = Kctl(False, 'staging')
        mocker.patch(
          'lib.kctl.Kctl.get_namespaced_object',
          return_value=mock_kubectl_get_configmaps_json_string
        )
        gno_spy = mocker.spy(lib.kctl.Kctl, 'get_namespaced_object')
        data = kctl.get_configmaps('foonamespace')
        gno_spy.assert_has_calls([
          mocker.call('configmaps', 'json', 'foonamespace')
        ])
        assert data == mock_kubectl_get_configmaps_json_object['items']

  def describe_get_secret():
    def it_gets_the_named_secret(mocker):
      kctl = Kctl(False, 'staging')
      mock_secret = {'foo': 'bar'}
      mocker.patch(
        'lib.kctl.Kctl.get_namespaced_object',
        return_value=json.dumps(mock_secret)
      )
      gno_spy = mocker.spy(lib.kctl.Kctl, 'get_namespaced_object')
      data = kctl.get_secret('foosecret', 'foonamespace')
      gno_spy.assert_has_calls([
        mocker.call('secrets', 'json', 'foonamespace', 'foosecret')
      ])
      assert data == mock_secret
