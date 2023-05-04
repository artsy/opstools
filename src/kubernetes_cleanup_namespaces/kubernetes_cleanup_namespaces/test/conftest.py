import os
import sys

## prepare environment before tests

# set env
os.environ['KUBECTL_CONTEXT'] = 'foo'

# set ndays command line argument
if len(sys.argv) == 2:
  # indicates that pytest is called with a dir path as argument
  # dir path becomes first argument to script
  # over-write it
  sys.argv[1] = '10'
else:
  # indicates that pytest is called with no argument
  # add argument
  sys.argv += ['10']
