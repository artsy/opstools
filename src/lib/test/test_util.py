from lib.util import (
  list_intersect,
  list_match_str,
  list_subtract
)

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
