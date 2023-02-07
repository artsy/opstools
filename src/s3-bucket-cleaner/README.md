# S3 Bucket Cleaner

This script `clean_s3_bucket.py` deletes S3 bucket objects, including those with lifecycle policies applied - in this case deletion markers also need to be deleted.

## Use

`python clean_s3_bucket.py`

### Required environment variables:

```
AWS_ACCESS_KEY_ID=iam-access-key
AWS_SECRET_ACCESS_KEY=iam-secret
S3_BUCKET=my-bucket
AWS_DEFAULT_REGION=default-aws-region
```

### Optional environment variables:

`S3_PREFIX=my-key-prefix` (if unset all objects in the bucket are deleted)


### Split the bucket cleaning into parallel Kubernetes Jobs

```
S3_BUCKET=my-bucket python create_jobs.py | kubectl --context staging apply -f -
```

### Clean a list of buckets.

If you want to do multiple buckets and the buckets are listed in a file, say, /tmp/list. You can do this:

```
cat /tmp/list | ./batch_clean.sh
```
`batch_clean.sh` takes care of some chores for you.


