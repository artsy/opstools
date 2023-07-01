import os
import sys

## prepare environment before tests, for pytest

# set command line arguments
if len(sys.argv) == 2:
  # indicates that pytest is called with a dir path as argument
  # dir path becomes first argument to script
  # over-write it
  sys.argv.pop()
  sys.argv += ['staging'] # artsy_env
  sys.argv += ['1'] # nhours
else:
  # indicates that pytest is called with no argument
  # add arguments
  sys.argv += ['staging'] # artsy_env
  sys.argv += ['1'] # nhours
