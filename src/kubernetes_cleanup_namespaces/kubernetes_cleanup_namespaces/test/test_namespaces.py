import kubernetes_cleanup_namespaces.namespaces

from kubernetes_cleanup_namespaces.namespaces import \
  config, \
  delete_namespaces, \
  kctl_client, \
  list_subtract, \
  old_namespaces, \
  over_ndays_ago, \
  unprotected_namespaces, \
  Kctl

from kubernetes_cleanup_namespaces.test.fixtures.namespaces import \
  mock_kctl_object, \
  mock_ns_object

def describe_delete_namespaces():
  def describe_force_set():
    def it_calls_delete_namespace(mock_kctl_object, mock_ns_object, mocker):
      mocker.patch.object(config, 'force', True)
      delete_namespace_spy = mocker.spy(mock_kctl_object, 'delete_namespace')
      delete_namespaces(['ns1', 'ns2'], mock_ns_object, mock_kctl_object)
      assert delete_namespace_spy.call_count == 2
      delete_namespace_spy.assert_has_calls([
        mocker.call('ns1'),
        mocker.call('ns2')
      ])
  def describe_force_unset():
    def it_does_not_call_delete_namespace(mock_kctl_object, mock_ns_object, mocker):
      mocker.patch.object(config, 'force', False)
      delete_namespace_spy = mocker.spy(mock_kctl_object, 'delete_namespace')
      delete_namespaces(['ns1', 'ns2'], mock_ns_object, mock_kctl_object)
      assert delete_namespace_spy.call_count == 0

def describe_kctl_client():
  def describe_no_context():
    def it_instantiates_with_none(mocker):
      mocker.patch.object(config, 'context', '')
      mocker.patch(
        'kubernetes_cleanup_namespaces.namespaces.Kctl.__init__'
      ).side_effect = [None]
      kctl_init_spy = mocker.spy(
        kubernetes_cleanup_namespaces.namespaces.Kctl, '__init__'
      )
      kctl = kctl_client()
      assert isinstance(kctl, Kctl)
      kctl_init_spy.call_count == 1
      kctl_init_spy.assert_has_calls([mocker.call(None)])
  def describe_context():
    def it_instantiates_with_context(mocker):
      mocker.patch.object(config, 'context', 'foo')
      mocker.patch(
        'kubernetes_cleanup_namespaces.namespaces.Kctl.__init__'
      ).side_effect = [None]
      kctl_init_spy = mocker.spy(
        kubernetes_cleanup_namespaces.namespaces.Kctl, '__init__'
      )
      kctl = kctl_client()
      assert isinstance(kctl, Kctl)
      kctl_init_spy.call_count == 1
      kctl_init_spy.assert_has_calls([mocker.call('foo')])

def describe_old_namespaces():
  def it_returns_only_old_namespaces(mock_ns_object, mocker):
    mocker.patch.object(config, 'ndays', 2)
    mocker.patch.object(mock_ns_object, 'created_at').side_effect = [
      'ns1_created_at',
      'ns2_created_at'
    ]
    mocker.patch(
      'kubernetes_cleanup_namespaces.namespaces.over_ndays_ago'
    ).side_effect = [
      True,
      False
    ]
    ona_spy = mocker.spy(
      kubernetes_cleanup_namespaces.namespaces, 'over_ndays_ago'
    )
    assert old_namespaces(['ns1', 'ns2'], mock_ns_object) == ['ns1']
    assert ona_spy.call_count == 2
    ona_spy.assert_has_calls([
      mocker.call('ns1_created_at', 2),
      mocker.call('ns2_created_at', 2)
    ])

def describe_unprotected_namespaces():
  def it_returns_only_unprotected_namespaces(mocker):
    mocker.patch.object(
      config,
      'protected_namespaces',
      ['ns1']
    )
    mocker.patch(
      'kubernetes_cleanup_namespaces.namespaces.list_subtract'
    ).side_effect = [['ns2']]
    list_subtract_spy = mocker.spy(
      kubernetes_cleanup_namespaces.namespaces,
      'list_subtract'
    )
    assert unprotected_namespaces(['ns1', 'ns2']) == ['ns2']
    assert list_subtract_spy.call_count == 1
    list_subtract_spy.assert_has_calls([
      mocker.call(['ns1', 'ns2'], ['ns1'])
    ])
