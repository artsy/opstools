def list_intersect(list_a, list_b):
  ''' return elements common between l1 and l2 '''
  return [ x for x in list_a if x in list_b]

def list_subtract(list_a, list_b):
  ''' return elements that are in list a but not b '''
  return [x for x in list_a if x not in list_b]

def list_match_str(list_a, str1):
  ''' return elements of list_a that match string str1 '''
  return [x for x in list_a if str1 in x]
