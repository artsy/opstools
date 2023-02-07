#!/usr/bin/env bash

# Input: stdin list of s3 buckets one per line.
# Output: none
# Action: Delete contents of s3 buckets.
#         Executes create_jobs.py/kubectl for each bucket.

ensure_bucket_empty() {
  S3_BUCKET="$1"

  # error out if bucket is not empty
  size=$(aws s3 ls --summarize --recursive s3://"$S3_BUCKET" | grep 'Total Size' | awk '{print $3}')
  if (( size != 0 ))
  then
    echo "Error: bucket size is not zero."
    exit 1
  else
    echo "bucket size is zero."
  fi
  
}

delete_s3_jobs() {
  for job in $(kubectl --context staging get jobs | grep s3-bucket | awk '{print $1}')
  do
    echo "deleting job: $job"
    kubectl --context staging delete jobs $job
  done
}

empty_out_bucket() {
  echo "operating on bucket $1"
  export S3_BUCKET="$1"

  # before lanching the jobs, ensure no jobs exist. otherwise, error out.
  n=$(kubectl --context staging get jobs | grep s3-bucket | wc -l)
  if (( n > 0 ))
  then
    echo "Error: there are existing s3 bucket clean up jobs. please delete them first."
    exit 1
  fi

  # TODO: add a check for bucket existence, allows write access, size. error out if it bucket is already empty.

  # launch the jobs.
  python create_jobs.py | kubectl --context staging apply -f -
  jobs_spawned=$(kubectl --context staging get jobs | grep s3-bucket | wc -l)
  echo "spawned $jobs_spawned jobs"

  # wait for jobs to complete.
  completed=0
  while [[ "$completed" != "$jobs_spawned" ]]
  do
    echo $(date) "continuously checking on jobs status until all jobs are in Completed status"
    completed=$(kubectl --context staging get pods | grep s3-bucket | grep Completed | wc -l)
    outstanding=$(( $jobs_spawned - $completed ))
    echo "$completed jobs completed. $jobs_spawned jobs outstanding."
    sleep 3
  done

  # confirm with user whether okay to delete the jobs.
  read -p "All jobs completed. Ready to delete them? Enter Y or y> " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]
  then
    echo "You said yes. Deleting!"
    delete_s3_jobs
  else
    echo "You didn't say yes. Not going to delete the jobs."
  fi
}

# Read in list of buckets.
while read bucket
do
  buckets+=("$bucket")
done < "${1:-/dev/stdin}"

# Switch STDIN to terminal. Rely on STDOUT being attached to terminal.
exec 0<&1

# Operate on 1 bucket at a time.
for bucket in "${buckets[@]}"
do
  # Get user confirmation.
  # TODO: Be more restrictive. Require answer of yes or no. Re-prompt until either is returned.
  read -p "You are about to delete everything in S3 bucket $bucket. Are you sure? Enter Y or y> " -n 1 -r
  echo

  if [[ $REPLY =~ ^[Yy]$ ]]
  then
    echo "You said yes. Deleting!"
    empty_out_bucket "$bucket"
    ensure_bucket_empty "$bucket"
  else
    echo "You didn't say yes. Skipping this bucket."
    continue
  fi
done

