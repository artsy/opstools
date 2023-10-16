#!/usr/bin/env python

# run this script from the root of a local repo of a hokusai-managed project
#
# edit a project's staging/production hokusai specs
# specifically on Kubernetes Deployment resources
# specifically their livenessProbe and readinessProbe configs
# specifically those that use 'exec' as probing method
# add timeoutSeconds to those probes if they don't have the setting
#
# for example, given the below livenessProbe that uses exec
# and a DESIRED_TIMEOUT_SECONDS of 3 seconds:
#
#        livenessProbe:
#          exec:
#            command:
#            - pgrep
#            - -f
#            - sidekiq
#          initialDelaySeconds: 30
#          periodSeconds: 30
#
# produce this:
#
#        livenessProbe:
#          exec:
#            command:
#            - pgrep
#            - -f
#            - sidekiq
#          initialDelaySeconds: 30
#          periodSeconds: 30
#          timeoutSeconds: 3

import glob
import os
import sys
import yaml

def probe(probe_type, container_spec):
  ''' add missing timeoutSeconds to any existing probe type that uses exec '''
  if probe_type in container_spec and 'exec' in container_spec[probe_type] and 'timeoutSeconds' not in container_spec[probe_type]:
        container_spec[probe_type]['timeoutSeconds'] = DESIRED_TIMEOUT_SECONDS

# adjust this to preference
DESIRED_TIMEOUT_SECONDS = 3

# all types  of probes in a Deployment spec
PROBE_TYPES = ['livenessProbe', 'readinessProbe']

base = 'hokusai'

# glob all staging.yml..., production.yml..., which might not exist
staging_files = glob.glob(base + '/staging.yml*')
prod_files = glob.glob(base + '/production.yml*')

tmpfile = base + '/tmp.yml'

for files in staging_files, prod_files:
  if files:
    # go with the first file
    path = files[0]
  else:
    # no files found, move on
    continue

  # figure env
  if 'staging' in path:
    env = 'staging'
  else:
    env = 'production'

  # read in spec content
  with open(path, 'r') as reader:
    spec_content = reader.read()

  # remove jinja syntax, otherwise yaml load fails
  spec_content = spec_content.replace('{{ ', 'doublecurlyspace')
  spec_content = spec_content.replace(' }}', 'spacedoublecurly')

  # parse yaml
  specobj = list(yaml.safe_load_all(spec_content))

  # patch
  for item in specobj:
    if item['kind'] == 'Deployment':
      container0_spec = item['spec']['template']['spec']['containers'][0]
      PROBE_TYPES = ['livenessProbe', 'readinessProbe']
      for type in PROBE_TYPES:
        probe(type, container0_spec)

  # write yaml
  with open(tmpfile, 'w') as writer:
    writer.write(yaml.safe_dump_all(specobj, sort_keys=False))

  # restore jinja syntax
  with open(tmpfile, 'r') as reader:
    tmp_content = reader.read()
  tmp_content = tmp_content.replace('doublecurlyspace', '{{ ')
  tmp_content = tmp_content.replace('spacedoublecurly', ' }}')
  with open(tmpfile, 'w') as writer:
    writer.write(tmp_content)

  # override spec
  os.replace(tmpfile, path)
