import os
import sys

## prepare environment before tests, for pytest

# set env
os.environ['GITHUB_TOKEN'] = 'footoken'
os.environ['REPOSDIRS'] = 'foorepo:foodir'

if len(sys.argv) == 2:
  # indicates that pytest is called with a dir path as argument
  # dir path becomes first argument to script
  # remove it
  sys.argv.pop()
else:
  # indicates that pytest is called with no argument
  pass
