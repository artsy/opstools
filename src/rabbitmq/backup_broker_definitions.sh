#!/bin/bash

set -e

echo "Exporting RabbitMQ Broker definitions..."
curl -H "Accept:application/json" -u $RABBITMQ_USER:$RABBITMQ_PASS https://$RABBITMQ_HOST/api/definitions > /tmp/$RABBITMQ_HOST-broker-definitions.json

echo  "Uploading to S3..."

aws s3 cp /tmp/$RABBITMQ_HOST-broker-definitions.json s3://$S3_BUCKET/$S3_PREFIX/$RABBITMQ_HOST-broker-definitions.json
rm /tmp/$RABBITMQ_HOST-broker-definitions.json

echo "Done!"
