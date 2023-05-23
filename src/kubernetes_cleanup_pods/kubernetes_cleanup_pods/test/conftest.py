import os
import sys

## prepare environment before tests, for pytest

# set env
os.environ['KUBECTL_CONTEXT'] = 'foo'

# set command line arguments
if len(sys.argv) == 2:
  # indicates that pytest is called with a dir path as argument
  # dir path becomes first argument to script
  # over-write it
  sys.argv[1] = '--name' # pod name option
  sys.argv += ['foo'] # pod name value
  sys.argv += ['1'] # nhours
else:
  # indicates that pytest is called with no argument
  # add arguments
  sys.argv += [
    '--name', # pod name option
    'foo', # pod name value
    '1' # nhours
  ]
