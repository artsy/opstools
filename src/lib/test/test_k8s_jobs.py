from dateutil.parser import parse as parsedatetime

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
        mocker.call('foo', 'job1')
      ])
  def describe_names():
    def it_returns_names_of_jobs(jobs_obj):
      assert jobs_obj.names() == ['job1', 'job2']
  def describe_completed_jobs_names():
    def it_returns_completed_jobs_names(jobs_obj):
      assert jobs_obj.completed_jobs_names() == ['job1']
  def describe_old_jobs_names():
    def it_returns_only_completed_jobs_names(jobs_obj): # excluding incomplete jobs
      old_date = parsedatetime('2023-05-17T03:00:00Z')
      assert jobs_obj.old_jobs_names(old_date) == ['job1']
    def it_returns_3_hours_old_jobs_names(jobs_obj): # including incomplete jobs
      old_date = parsedatetime('2023-05-17T03:00:00Z')
      assert jobs_obj.old_jobs_names(old_date, True) == ['job1', 'job2']
