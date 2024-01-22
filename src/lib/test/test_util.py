import glob
import os
import pytest
import subprocess

from lib.util import (
  config_secret_sanitizer_artsy,
  config_secret_sanitizer_eso,
  dict1_in_dict2,
  is_artsy_s3_bucket,
  is_quoted,
  list_intersect,
  list_match_str,
  list_subtract,
  match_or_raise,
  parse_string_of_key_value_pairs,
  replace_dashes_in_dict_keys_with_underscores,
  run_cmd,
  search_dirs_by_suffix,
  unquote,
  write_file
)

def describe_config_secret_sanitizer_artsy():
  def it_removes_surrounding_quotes():
    assert config_secret_sanitizer_artsy('"foo"') == 'foo'

def describe_config_secret_sanitizer_eso():
  def it_adds_double_quotes_when_special_yaml_char():
    assert config_secret_sanitizer_eso('*foo') == '"*foo"'
  def it_returns_same_string_otherwise():
    assert config_secret_sanitizer_eso('foo') == 'foo'

def describe_dict1_in_dict2():
  def it_returns_true_when_dict1_is_in_dict2():
    dict1 = {
      'foo': 'bar'
    }
    dict2 = {
      'foo': 'bar',
      'bar': 'baz'
    }
    assert dict1_in_dict2(dict1, dict2)
  def it_returns_false_when_dict1_is_not_in_dict2():
    dict1 = {
      'foo': 'bin'
    }
    dict2 = {
      'foo': 'bar',
      'bar': 'baz'
    }
    assert not dict1_in_dict2(dict1, dict2)
  def it_returns_true_when_dict1_is_empty_and_dict2_not():
    dict1 = {}
    dict2 = {
      'foo': 'bar',
      'bar': 'baz'
    }
    assert dict1_in_dict2(dict1, dict2)
  def it_returns_false_when_dict2_is_empty_and_dict1_not():
    dict1 = {
      'foo': 'bin'
    }
    dict2 = {}
    assert not dict1_in_dict2(dict1, dict2)
  def it_returns_true_when_both_empty():
    dict1 = {}
    dict2 = {}
    assert dict1_in_dict2(dict1, dict2)

def describe_is_artsy_s3_bucket():
  def it_returns_true_if_name_starts_with_artsy():
    assert is_artsy_s3_bucket('artsy-foo-bucket')
  def it_returns_false_if_name_does_not_start_with_artsy():
    assert not is_artsy_s3_bucket('foo-bucket')
  def it_returns_false_if_name_is_empty_string():
    assert not is_artsy_s3_bucket('')

def describe_is_quoted():
  def it_returns_double_quote_when_string_is_quoted_that():
    assert is_quoted('"foo"') == '"'
  def it_returns_single_quote_when_string_is_quoted_that():
    assert is_quoted("'foo'") == "'"
  def it_does_not_return_when_string_is_not_quoted():
    assert is_quoted('foo') == None
  def it_ignores_non_surrounding_quotes():
    assert is_quoted('"foo') == None

def describe_list_intersect():
  def it_returns_common_elements():
    a = [1, 2, 3]
    b = [3, 4, 5]
    assert list_intersect(a,b) == [3]

def describe_list_match_str():
  def it_returns_matching_elements():
    str1 = 'foo'
    a = ['foo', 'foobar', 'barfoo', 'baz', 'boo']
    assert list_match_str(a, str1) == [
      'foo', 'foobar', 'barfoo'
    ]

def describe_list_subtract():
  def it_returns_a_when_nothing_to_subtract():
    a = [1, 2, 3]
    assert list_subtract(a) == a
  def it_subtracts_one():
    a = [1, 2, 3]
    b = [1, 3]
    assert list_subtract(a,b) == [2]
  def it_subtracts_multiple():
    a = [1, 2, 3, 4]
    b = [1, 3]
    c = [2]
    assert list_subtract(a,b,c) == [4]
  def it_ignores_elements_not_in_a():
    a = [1, 2, 3]
    b = [1, 3, 4, 5]
    assert list_subtract(a,b) == [2]

def describe_match_or_raise():
  def it_does_not_raise_when_match():
    assert match_or_raise('foo', 'foo') is None
  def it_raises_when_no_match():
    with pytest.raises(Exception):
      assert match_or_raise('foo', 'bar')

def describe_parse_string_of_key_value_pairs():
  def it_parses():
    kv_string = 'foo:x,foo:y,bar:x'
    assert parse_string_of_key_value_pairs(kv_string) == {
      'foo': ['x', 'y'],
      'bar': ['x']
    }

def describe_replace_dashes_in_dict_keys_with_underscores():
  def it_replaces():
    dict1 = {
      'foo': 'bar',
      'foo-foo': 'bar'
    }
    dict2 = {
      'foo': 'bar',
      'foo_foo': 'bar'
    }
    new_dict = replace_dashes_in_dict_keys_with_underscores(dict1)
    assert new_dict == dict2

def describe_run_cmd():
  def it_runs(tmp_path):
    os.chdir(tmp_path)
    os.makedirs('foo')
    resp = run_cmd('ls', tmp_path)
    assert resp.stdout == 'foo\n'
    assert resp.returncode == 0
  def it_does_not_timeout(tmp_path):
    os.chdir(tmp_path)
    resp = run_cmd('sleep 1', tmp_path, timeout=3)
  def it_times_out(tmp_path):
    with pytest.raises(subprocess.TimeoutExpired):
      os.chdir(tmp_path)
      resp = run_cmd('sleep 3', tmp_path, timeout=1)

def describe_search_dirs_by_suffix():
  def it_returns_dirs_that_have_matching_files(tmp_path):
    os.chdir(tmp_path)
    os.makedirs('foo')
    os.makedirs('bar/bar')
    os.makedirs('baz')
    open('foo/file.txt', 'w').close()
    open('bar/bar/file.txt', 'w').close()
    open('baz/file.gz', 'w').close()
    expected_dirs = [
      os.path.join(tmp_path, 'bar/bar'),
      os.path.join(tmp_path, 'foo')
    ]
    assert search_dirs_by_suffix(tmp_path, 'txt') == expected_dirs

def describe_unquote():
  def it_removes_surrounding_double_quotes():
    assert unquote('"foo"') == 'foo'
  def it_removes_surrounding_single_quotes():
    assert unquote("'foo'") == 'foo'
  def it_returns_same_string_if_unquoted():
    assert unquote('"foo') == '"foo'

def describe_write_file():
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
