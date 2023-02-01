from terraform_drift_detection.util import abort_on_nonzero_exit, run_cmd

def clone_repo(repo, dirx):
  ''' git clones a repo '''
  cmd = 'git clone git@github.com:artsy/' + repo + '.git'
  output = run_cmd(cmd, dirx)
  abort_on_nonzero_exit(cmd, output.returncode)
