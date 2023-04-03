#!/usr/bin/env python

# run this script from the root of a local repo of a hokusai-managed project
#
# edit a project's staging/production hokusai specs
# add the following to each k8s deployment resource
#
# - version label
#
#     app.kubernetes.io/version: production
#
# - DD_VERSION env var
#
#     env:
#     - name: DD_VERSION
#       valueFrom:  
#         fieldRef:                    
#           fieldPath: metadata.labels['app.kubernetes.io/version']

import glob
import os
import sys
import yaml

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
      item['metadata']['labels']['app.kubernetes.io/version'] = env
      item['spec']['template']['metadata']['labels']['app.kubernetes.io/version'] = env

      if 'env' in item['spec']['template']['spec']['containers'][0]:
        item['spec']['template']['spec']['containers'][0]['env'].append(
          { 'name': 'DD_VERSION',
            'valueFrom': {
              'fieldRef': {
                'fieldPath': "metadata.labels['app.kubernetes.io/version']"
              }
            }
          }
        )
      else:
        item['spec']['template']['spec']['containers'][0]['env'] = [
          { 'name': 'DD_VERSION',
            'valueFrom': {
              'fieldRef': {
                'fieldPath': "metadata.labels['app.kubernetes.io/version']"
              }
            }
          }
        ]

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
