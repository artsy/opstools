# manage.sh

There is a playbook on how to migrate an app from one RDS instance to another using pglogical.

https://www.notion.so/artsy/Migrate-application-from-one-RDS-Postgres-instance-to-another-using-pglogical-4efadac132a54c0a97c1cf8e09eab8a4

The section on `Migrate App` contains some tedious steps which this script automates.

## Dependencies

- Docker. The script runst postgres docker images to connect to DB hosts.
- VPN. To staging/production. The script connects to old and new DB hosts.

