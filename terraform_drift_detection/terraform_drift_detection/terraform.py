import glob
import os

from terraform_drift_detection.util import abort_on_nonzero_exit, run_cmd

def find_tf_dirs(dirx):
  ''' return list of sub dirs that have .tf files '''
  globstr = dirx + '/**/*.tf'
  tf_files = [
    path for path in glob.glob(globstr, recursive=True)
    if os.path.isfile(path)
  ]
  tf_dirs = [os.path.dirname(path) for path in tf_files]
  return sorted(list(set(tf_dirs)))

def tf_in_repo_dir(dirx):
  ''' run terraform commands in dir '''
  init_cmd = 'terraform init'
  plan_cmd = 'terraform plan -detailed-exitcode'
  output = run_cmd(init_cmd, dirx)
  abort_on_nonzero_exit(init_cmd, output.returncode)
  output = run_cmd(plan_cmd, dirx)
  if output.returncode == 0:
    print('INFO: terraform plan suceeded and reported no changes.')
  else:
    print('ERROR: there is possibly drift between tf plans and cloud config.')
    abort_on_nonzero_exit(plan_cmd, output.returncode)
