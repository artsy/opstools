Script to back up RabbitMQ broker definitions to S3.

Run script for staging RabbitMQ as follows:

- Connect to staging VPN.
- Assuming .env.shared exists in repo root dir (see bin/setup), load its vars into env:
    at repo root dir:
    export $(cat .env.shared | grep -v ^# | xargs)
- Run script:
    ./backup_broker_definitions.sh
