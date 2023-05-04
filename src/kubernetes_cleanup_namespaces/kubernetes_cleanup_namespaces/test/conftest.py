import os
import sys

# prepare environment before tests
os.environ['KUBECTL_CONTEXT'] = 'foo'
sys.argv += ['10'] # corresponds to ndays command line argument
