#!/usr/bin/env bash

set -e

# migrate a job from ec2 jenkins to k8s jenkins.

function check_input() {
  if !(( $# == 2 ))
  then
    usage
    exit 1
  fi
}

function usage() {
  cat << EOF
    Usage: $0 job

    ec2ip - IP of EC2 Jenkins to migrate job from.
    job - name of the jenkins job
EOF
}

check_input "$@"

NEW_JENKINS_DNS=<new-jenkins-dns>
JENKINS_EC2=$1
JOB_NAME=$2

JOB_DIR=jobs/"$JOB_NAME"
mkdir -p "$JOB_DIR"

SUFFIX=`date +%Y%m%d%H%M%S -u`
FILE_NAME=config.xml."$SUFFIX"
DISABLED_FILE_NAME="$FILE_NAME.disabled"

# identify pod name
JENKINS_POD=`kubectl --context production get pods | grep jenkins | awk '{print $1}'`

# find out whether this job is referred to in other jobs' configs.
echo "all job configs that reference job name"
# so that grep no result does not abort script.
set +e
ssh "$JENKINS_EC2" grep -l $JOB_NAME /var/lib/jenkins/jobs/*/config.xml
set -e

# get job config from ec2 jenkins
scp "$JENKINS_EC2":/var/lib/jenkins/jobs/"$JOB_NAME"/config.xml "$JOB_DIR/$FILE_NAME"

# mark job as disabled in config.
# but first ensure that it is not already disabled.
if (grep '<disabled>true</disabled>' "$JOB_DIR/$FILE_NAME")
then
  echo "job is already disabled"
  SRC_FILE="$JOB_DIR/$FILE_NAME"
else
  sed 's|<disabled>false</disabled>|<disabled>true</disabled>|' "$JOB_DIR/$FILE_NAME" > "$JOB_DIR/$DISABLED_FILE_NAME"
  SRC_FILE="$JOB_DIR/$DISABLED_FILE_NAME"
fi

# copy job config to k8s jenkins.
kubectl --context production exec -it "$JENKINS_POD" -- mkdir /var/lib/jenkins/jobs/"$JOB_NAME"
kubectl --context production cp "$SRC_FILE" "$JENKINS_POD":/var/lib/jenkins/jobs/"$JOB_NAME"/config.xml

# manual steps.
cat <<EOF

Perform these manual steps:

1) Pre-pend this to job description on old Jenkins.

<p style="font-size:30px">
!!! Alert !!!
This job moved to: <a href="https://$NEW_JENKINS_DNS/job/$JOB_NAME/">$NEW_JENKINS_DNS</a>
</p>

2) Disable job on old Jenkins, if it's not already disabled.

3) Reload config on new Jenkins.

Manage Jenkins -> Reload Configuration from Disk

4) Check job config on new Jenkins, uncomment any virtualenv steps (they were added temporarily on old Jenkins due to PyPA SNI deprecation.)

5) Set "Delete workspace before build starts" job config on new Jenkins. To overcome new Jenkins newer Git version refuses to over-write repo's tags.

6) Enable job on new Jenkins, only if it was in enabled state on old Jenkins.

EOF
