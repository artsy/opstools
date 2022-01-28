This README describes the function of each script stored in this directory.

They are meant to be run by a wrapper script one level up in the dir tree.

# add_ingress.py

Created for the ELB->Ingress migration.

Adds a -web-internal Service and Ingress resource to a hokusai-enabled app's staging and production config, prompting for input.

Use: `python add_ingress.py ../path/to/project/root` and respond to prompts for user input.

Example:
```
(opstools) isacpetruzzi@Artsy-Isac hokusai-app-updater (fea-hokusai-app-updater) $ python add_ingress.py ../../positron
Editing ../../positron/hokusai/staging.yml ...
Enter the service name ( default: positron ) -->
Enter the service port ( default: 8080 ) -->
Is this service behond cloudflare? [y/n] --> n
Enter the hostname ( default: positron.artsy.net ) --> stagingwriter.artsy.net
Editing ../../positron/hokusai/production.yml ...
Enter the service name ( default: positron ) -->
Enter the service port ( default: 8080 ) -->
Is this service behond cloudflare? [y/n] --> y
Enter the hostname ( default: positron.artsy.net ) --> writer.artsy.net

# remove_elb_nginx_sidecar.py

Created for the ELB->Ingress migration.

Updates a hokusai-enabled app's staging and production config, to remove its ELB service and Nginx sidecar.
