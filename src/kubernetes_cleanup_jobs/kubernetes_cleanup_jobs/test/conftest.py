import os
import sys

## prepare environment before tests, for pytest

# set env
os.environ['KUBECTL_CONTEXT'] = 'foo'

# set nhours command line argument
if len(sys.argv) == 2:
  # indicates that pytest is called with a dir path as argument
  # dir path becomes first argument to script
  # over-write it
  sys.argv[1] = '1' # pod name argument
else:
  # indicates that pytest is called with no argument
  # add argument
  sys.argv += [
    '1' # nhours
  ]