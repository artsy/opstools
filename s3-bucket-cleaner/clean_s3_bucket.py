#!/usr/bin/env python

# Sourced from https://gist.github.com/seventhskye/0cc7b2804252975d36dca047ab7729e9 with some modifications

import os
import boto3

def main():
  client = boto3.client('s3')
  Bucket = os.environ.get('S3_BUCKET')
  Prefix = os.environ.get('S3_PREFIX', '') # leave blank to delete the entire contents
  IsTruncated = True
  MaxKeys = 1000
  KeyMarker = None

  if Bucket is None:
    print("Environment variable S3_BUCKET must be set!")
    return

  while IsTruncated == True:
    if not KeyMarker:
      version_list = client.list_object_versions(
              Bucket=Bucket,
              MaxKeys=MaxKeys,
              Prefix=Prefix)
    else:
      version_list = client.list_object_versions(
              Bucket=Bucket,
              MaxKeys=MaxKeys,
              Prefix=Prefix,
              KeyMarker=KeyMarker)

    try:
      objects = []
      versions = version_list['Versions']
      for v in versions:
              objects.append({'VersionId':v['VersionId'],'Key': v['Key']})
      response = client.delete_objects(Bucket=Bucket,Delete={'Objects':objects})
      for item in response['Deleted']:
        print("Deleted %s" % item['Key'])
    except:
      pass

    try:
      objects = []
      delete_markers = version_list['DeleteMarkers']
      for d in delete_markers:
              objects.append({'VersionId':d['VersionId'],'Key': d['Key']})
      response = client.delete_objects(Bucket=Bucket,Delete={'Objects':objects})
      for item in response['Deleted']:
        print("Deleted %s" % item['Key'])
    except:
      pass

    IsTruncated = version_list['IsTruncated']
    if 'NextKeyMarker' in version_list:
      KeyMarker = version_list['NextKeyMarker']

if __name__ == '__main__':
  main()
