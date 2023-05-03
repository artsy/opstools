def list_subtract(list_a, list_b):
  ''' return list of elements that are in list a but not in list b '''
  return [x for x in list_a if x not in list_b]
