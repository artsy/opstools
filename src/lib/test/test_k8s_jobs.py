from lib.test.fixtures.kctl import (
  mock_kctl,
  mock_kubectl_get_namespaces_json_object, # indirect usage
  mock_kubectl_get_pods_json_object, # indirect usage
  mock_kubectl_get_jobs_json_object
)

from lib.test.fixtures.k8s_jobs import jobs_obj

def describe_jobs():

  def describe_instantiation():
    def it_stores_data(
        mock_kctl,
        mock_kubectl_get_jobs_json_object,
        jobs_obj
      ):
        assert jobs_obj._kctl is mock_kctl
        assert jobs_obj._namespace == 'foo'
        assert jobs_obj._jobs_data == mock_kubectl_get_jobs_json_object['items']

  def describe_delete():
    def it_calls_kctl_delete_job(mock_kctl, mocker, jobs_obj):
      kctl_spy = mocker.spy(mock_kctl, 'delete_job')
      jobs_obj.delete('job1')
      assert kctl_spy.call_count == 1
      kctl_spy.assert_has_calls([
        mocker.call('job1', 'foo')
      ])

  def describe_old_jobs():
    def it_returns_only_old_jobs(jobs_obj, mocker):
      mocker.patch(
        'lib.k8s_jobs.over_nhours_ago'
      ).side_effect = [False, True]
      assert jobs_obj.old_jobs(10) == ['job2']
