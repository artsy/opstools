#!/usr/bin/env bash

# Script to request Let's Encrypt for an SSL cert for a specific domain.
#
# Example domains:
#
#   - www.example.com
#   - *.example.com
#   - www.foo.example.com
#   - *.foo.example.com

set -e

function usage() {
  cat << EOF
    Usage: $0

    Please ensure these vars are set in env:

      CERT_DOMAIN - The domain to request cert for. Example: 'www.example.com'

      CERT_S3_BUCKET - Name of the S3 bucket to save the cert in.
                  For example, if domain is 'www.example.com',
                  and the S3 bucket is 'secret-bucket', the cert will be saved in:
                  s3://secret-bucket/certificates/www.example.com/"

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

echo "Requesting cert for domain: $CERT_DOMAIN."
echo "Cert will be saved in: $S3_LOCATION"

echo "Creating certbot dirs under your home dir..."
CERTBOT_DIR=~/certbot
CERTBOT_ETC_DIR=~/certbot/etc
CERTBOT_VAR_DIR=~/certbot/lib
CERTBOT_CERT_DIR="~/certbot/etc/live/$CERT_DOMAIN"
mkdir -p "$CERTBOT_ETC_DIR"
mkdir -p "$CERTBOT_VAR_DIR"

cat << EOF
Running certbot, follow interactive prompts. See README for how to answer prompts.

When prompted, provide certbot the domain: $CERT_DOMAIN
To prove that you own the domain, certbot will ask you to create the following TXT record:

_acme-challenge.$CERT_DOMAIN

Go to the DNS provider (Cloudflare, Route53, ...) and create it. Then confirm that it exists, using dig/nslookup.

Certbot will generate the cert/key and save them in $CERTBOT_CERT_DIR

EOF

docker run -it --rm --name certbot \
  -v "$CERTBOT_ETC_DIR:/etc/letsencrypt"  \
  -v "$CERTBOT_VAR_DIR:/var/lib/letsencrypt" \
  certbot/certbot certonly --manual --force-renewal --preferred-challenges=dns

read -p "The TXT record that you created are no longer required. Please delete them. Hit enter when done."

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

echo "For security, please delete certbot files from your home dir when you have finished working with them."
