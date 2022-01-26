Convenience script to request a certificate from Let's Encrypt using the Certbot tool and upload to Artsy's kubernetes clusters.

# Requirements
- AWS CLI
- Docker

# Run like:

```bash
./cert.sh
```

Here's a sample run of the Certbot step that requests a cert for *.foo.bar/*.prd.foo.bar/*.stg.foo.bar:

```
$ docker run -it --rm --name certbot \
    -v "$CERTBOT_ETC_DIR:/etc/letsencrypt"  \
    -v "$CERTBOT_VAR_DIR:/var/lib/letsencrypt" \
    certbot/certbot certonly --manual --force-renewal --preferred-challenges=dns

Saving debug log to /var/log/letsencrypt/letsencrypt.log
Plugins selected: Authenticator manual, Installer None
Enter email address (used for urgent renewal and security notices)
 (Enter 'c' to cancel): ops@foo.bar

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Please read the Terms of Service at
https://letsencrypt.org/documents/LE-SA-v1.2-November-15-2017.pdf. You must
agree in order to register with the ACME server. Do you agree?
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: Y

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Would you be willing, once your first certificate is successfully issued, to
share your email address with the Electronic Frontier Foundation, a founding
partner of the Let's Encrypt project and the non-profit organization that
develops Certbot? We'd like to send you email about our work encrypting the web,
EFF news, campaigns, and ways to support digital freedom.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: N
Account registered.
Please enter in your domain name(s) (comma and/or space separated)  (Enter 'c'
to cancel): *.foo.bar,*.prd.foo.bar,*.stg.foo.bar
Requesting a certificate for *.foo.bar and 2 more domains
Performing the following challenges:
dns-01 challenge for foo.bar
dns-01 challenge for prd.foo.bar
dns-01 challenge for stg.foo.bar

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Please deploy a DNS TXT record under the name
_acme-challenge.foo.bar with the following value:

<snip>

Before continuing, verify the record is deployed.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Press Enter to Continue

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Please deploy a DNS TXT record under the name
_acme-challenge.prd.foo.bar with the following value:

<snip>

Before continuing, verify the record is deployed.
(This must be set up in addition to the previous challenges; do not remove,
replace, or undo the previous challenge tasks yet. Note that you might be
asked to create multiple distinct TXT records with the same name. This is
permitted by DNS standards.)

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Press Enter to Continue

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Please deploy a DNS TXT record under the name
_acme-challenge.stg.foo.bar with the following value:

<snip>

Before continuing, verify the record is deployed.
(This must be set up in addition to the previous challenges; do not remove,
replace, or undo the previous challenge tasks yet. Note that you might be
asked to create multiple distinct TXT records with the same name. This is
permitted by DNS standards.)

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Press Enter to Continue
Waiting for verification...
Cleaning up challenges

IMPORTANT NOTES:
 - Congratulations! Your certificate and chain have been saved at:
   /etc/letsencrypt/live/foo.bar/fullchain.pem
   Your key file has been saved at:
   /etc/letsencrypt/live/foo.bar/privkey.pem
   Your certificate will expire on 2021-06-03. To obtain a new or
   tweaked version of this certificate in the future, simply run
   certbot again. To non-interactively renew *all* of your
   certificates, run "certbot renew"
 - If you like Certbot, please consider supporting our work by:

   Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
   Donating to EFF:                    https://eff.org/donate-le
```
