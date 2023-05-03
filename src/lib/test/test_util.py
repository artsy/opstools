from lib.util import \
  list_subtract

def describe_list_subtract():
  def it_subtracts_when_a_is_superset_of_b():
    a = [1, 2, 3]
    b = [1, 3]
    assert list_subtract(a,b) == [2]
  def it_ignores_elements_in_b_not_in_a():
    a = [1, 2, 3]
    b = [1, 3, 4, 5]
    assert list_subtract(a,b) == [2]
