import glob
import logging
import os
import subprocess

def is_artsy_s3_bucket(name):
  ''' return true if bucket name starts with artsy- '''
  return name.startswith('artsy-')

def list_intersect(list_a, list_b):
  ''' return elements common between l1 and l2 '''
  return [ x for x in list_a if x in list_b]

def list_subtract(list_a, *args):
  '''
  return elements that are in list a but
  not in any list supplied by *args
  '''
  minuend = list_a
  for subtrahend in args:
    minuend = [x for x in minuend if x not in subtrahend]
  return minuend

def list_match_str(list_a, str1):
  ''' return elements of list_a that match string str1 '''
  return [x for x in list_a if str1 in x]

def run_cmd(cmd, dirx):
  ''' run command in dir and return output '''
  os.chdir(dirx)
  logging.info(f"running {cmd} command in {dirx} directory.")
  output = subprocess.run(
    cmd,
    capture_output=True,
    shell=True,
    text=True,
    timeout=300
  )
  logging.info(
    f"{cmd} command exited with code {output.returncode}"
  )
  return output

def search_dirs_by_suffix(dirx, suffix):
  ''' return dirx's subdirs that contain files with the given suffix '''
  globstr = f"{dirx}/**/*.{suffix}"
  files = [
    path for path in glob.glob(globstr, recursive=True)
    if os.path.isfile(path)
  ]
  dirs = [os.path.dirname(path) for path in files]
  return sorted(list(set(dirs)))
