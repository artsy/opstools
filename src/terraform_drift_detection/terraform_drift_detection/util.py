import logging
import os
import subprocess

from enum import Enum

class Drift(Enum):
  ''' enumerate terraform drift detection results '''
  NODRIFT = 0
  DRIFT = 1
  UNKNOWN = 2

def run_cmd(cmd, dirx):
  ''' run command in dir and return output '''
  os.chdir(dirx)
  logging.info('running "%s" command in "%s" directory.', cmd, dirx)
  output = subprocess.run(cmd, shell=True, text=True, capture_output=True)
  logging.info('"%s" command exited with code "%s".', cmd, output.returncode)
  return output
