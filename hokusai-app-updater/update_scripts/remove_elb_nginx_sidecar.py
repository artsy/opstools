import os
import re

import argparse

YAML_SEPARATOR = '---'

EDIT_FILES = [
  'hokusai/staging.yml',
  'hokusai/staging.yml.j2',
  'hokusai/production.yml',
  'hokusai/production.yml.j2'
]

def main(projects):
  for project in projects:
    project_name = os.path.normpath(project).split(os.sep)[-1]
    for file in EDIT_FILES:
      filename = os.path.join(project, file)
      if not os.path.isfile(filename):
        continue

      print("Editing %s ..." % filename)
      with open(filename, 'r') as f:
        struct = f.read()

        # Remove ELB service
        regex = re.compile("^---\napiVersion:\sv1\nkind:\sService\nmetadata:\n\s*labels:\n\s*app: %s.*type: LoadBalancer\n" % project_name, flags=re.DOTALL | re.MULTILINE)
        struct = re.sub(regex, '', struct)

        # Remove Nginx Sidecar and SSL Certs volume from Pod spec
        regex = re.compile("^\s*-\sname:\s%s-nginx.*defaultMode:\s420\n" % project_name, flags=re.DOTALL | re.MULTILINE)
        struct = re.sub(regex, '', struct)

      with open(filename, 'w') as f:
        f.write(struct)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Projects to update')
  parser.add_argument('projects', type=str, nargs='+')
  main(parser.parse_args().projects)
