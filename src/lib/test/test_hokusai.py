import lib.hokusai

from lib.hokusai import env_unset


def describe_env_unset():
  def it_calls_run_properly(mocker):
    mocker.patch('lib.hokusai.run_cmd')
    spy = mocker.spy(lib.hokusai, 'run_cmd')
    calls = [
      mocker.call(
        'hokusai fooenv env unset foo',
        'foodir'
      ),
    ]
    env_unset('foodir', 'fooenv', 'foo')
    spy.assert_has_calls(calls, any_order=True)
