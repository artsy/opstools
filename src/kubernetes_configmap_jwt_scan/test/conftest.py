import sys

## prepare environment before tests, for pytest

if len(sys.argv) == 2:
  # indicates that pytest is called with a dir path as argument
  # dir path becomes first argument to script
  # remove it
  sys.argv.pop()
else:
  # indicates that pytest is called with no argument
  pass

# add required command line args
sys.argv += ['staging'] # artsy_env
