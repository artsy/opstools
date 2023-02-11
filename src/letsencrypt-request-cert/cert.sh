#!/usr/bin/env bash

set -e

function usage() {
  cat << EOF
    Usage: $0

    Please ensure these vars are set in env:

      CERT_DOMAIN - The domain to request certs for.
               For example, if domain is foo.bar, certs will be requested for:
               *.foo.bar, *.prd.foo.bar, *.stg.foo.bar

      CERT_S3_BUCKET - Name of the S3 bucket to save the certs in.
                  For example, if domain is foo.bar, and S3 bucket is 'foobar-data', the certs will be saved in:
                  s3://foobar-data/certificates/foo.bar/"

    Did you run setup and load the env vars? See project README.md for more info.
EOF
}

# make sure vars are set in the env
if [[ "$CERT_DOMAIN" == '' ]] || [[ "$CERT_S3_BUCKET" == '' ]]
then
  usage
  exit 1
fi

S3_LOCATION="s3://$CERT_S3_BUCKET/certificates/$CERT_DOMAIN/"
CERT_DOMAINS="*.$CERT_DOMAIN,*.prd.$CERT_DOMAIN,*.stg.$CERT_DOMAIN"

echo "Requesting certs for domains: $CERT_DOMAINS"
echo "They will be saved in: $S3_LOCATION"

echo "Creating certbot dirs under your home dir..."
CERTBOT_DIR=~/certbot
CERTBOT_ETC_DIR=~/certbot/etc
CERTBOT_VAR_DIR=~/certbot/lib
CERTBOT_CERT_DIR="~/certbot/etc/live/$CERT_DOMAIN"
mkdir -p "$CERTBOT_ETC_DIR"
mkdir -p "$CERTBOT_VAR_DIR"

cat << EOF
Running certbot, follow interactive prompts. See README for how to answer prompts.

When prompted, provide to certbot these domains: $CERT_DOMAINS
To prove that you own those domains, certbot will ask you to create the following TXT records:

_acme-challenge.$CERT_DOMAIN
_acme-challenge.prd.$CERT_DOMAIN
_acme-challenge.stg.$CERT_DOMAIN

Go to Route53, create them all under '$CERT_DOMAIN' hosted zone. (not under prd/stg.$CERT_DOMAIN zones)

After you create each record, verify it exists using dig/nslookup. (make sure you are not on VPN otherwise you won't see the record)

Certbot will generate cert/key and save them in $CERTBOT_CERT_DIR

EOF

docker run -it --rm --name certbot \
  -v "$CERTBOT_ETC_DIR:/etc/letsencrypt"  \
  -v "$CERTBOT_VAR_DIR:/var/lib/letsencrypt" \
  certbot/certbot certonly --manual --force-renewal --preferred-challenges=dns

read -p "The TXT records that you created are no longer required. Please delete them. Hit enter when done."

echo "Files generated by Certbot are owned by root. Changing ownership to you (via sudo)..."
USER=$(id -u)
GROUP=$(id -g)
sudo chown -R "$USER":"$GROUP" "$CERTBOT_ETC_DIR"
sudo chown -R "$USER":"$GROUP" "$CERTBOT_VAR_DIR"

echo "Tar up Certbot files..."
DAY=$(date +%Y%m%d)
TAR_FILE="$CERTBOT_DIR/certbot.$DAY.tar.gz"
tar -czvvf "$TAR_FILE" "$CERTBOT_DIR"

echo "Ship the tar up to $S3_LOCATION which currently has:"
aws s3 ls "$S3_LOCATION" || echo "Something wrong with executing AWS CLI."
aws s3 cp "$TAR_FILE" "$S3_LOCATION"

K8S_SECRET_NAME=$(echo $CERT_DOMAIN | sed 's/\./-/g')-tls
CERT_DIR="$CERTBOT_ETC_DIR/archive/$CERT_DOMAIN/fullchain1.pem"
KEY_DIR="$CERTBOT_ETC_DIR/archive/$CERT_DOMAIN/privkey1.pem"

echo "Loading new cert/key into staging k8s for use by ingress controllers..."
kubectl --context staging delete secret "$K8S_SECRET_NAME"
kubectl --context staging create secret tls "$K8S_SECRET_NAME" \
  --cert="$CERT_DIR" \
  --key="$KEY_DIR"

echo "Go visit https://kubernetes.stg.$CERT_DOMAIN and check out the cert."
read -p "Hit enter if the cert is good."
read -p "You said cert is good. I am ready to repeat for prod k8s. Hit enter to proceed."

echo "Loading new cert/key into production k8s for use by ingress controllers..."
kubectl --context production delete secret "$K8S_SECRET_NAME"
kubectl --context production create secret tls "$K8S_SECRET_NAME" \
  --cert="$CERT_DIR" \
  --key="$KEY_DIR"

echo "Go visit https://kubernetes.prd.$CERT_DOMAIN and check out the cert."

echo "Deleting certbot files from your home dir..."
rm -rf ~/certbot