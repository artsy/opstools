def list_subtract(list_a, list_b):
  ''' return elements that are in list a but not b '''
  return [x for x in list_a if x not in list_b]
