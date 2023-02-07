#!/usr/bin/env python

import os
import string
import subprocess

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from jinja2.exceptions import TemplateError


def main():
  for prefix in list(range(0,10)) + list(string.ascii_lowercase):
    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')), undefined=StrictUndefined)
    template = env.get_template('job.yml.j2')
    context = {
      'job_name': "s3-bucket-cleaner-%s" % prefix,
      's3_bucket': os.environ.get('S3_BUCKET'),
      's3_prefix': prefix,
      'aws_access_key_id': os.environ.get('AWS_ACCESS_KEY_ID'),
      'aws_secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
      'aws_default_region': os.environ.get('AWS_DEFAULT_REGION')
    }
    print(template.render(**context))

if __name__ == "__main__":
  main()
