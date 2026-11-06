# `rotate.sh`

Rotates an App Trust token: a JWT minted by Gravity that one app uses to call another. The token lives in Vault at `kvv2/kubernetes/apps/<app>/<KEY>`. The weekly JWT expiration scan ([`list_vault_jwt_expiration`](../list_vault_jwt_expiration)) fails when a token's `expires_at` metadata is less than 30 days away. This script is what you run when that happens.

It automates the Notion playbook "How to rotate an App Trust Token":

1. **Preflight (read-only):** checks tools, the Vault address for the env, VPN and a Vault login, and write capability. It reads the current token and takes the audience (`aud`) and subject (`subject_application`) from its claims, so you never type IDs.
2. **Mint:** runs `hokusai <env> run 'bundle exec rake token[aud,sub,1y]'` in Gravity.
3. **Verify:** the new token decodes, differs from the old one, has identical non-time claims, and expires in about 1 year.
4. **Write:** runs `vault kv patch` for the key (other keys are kept), then `vault kv metadata patch` to set `expires_at` (other metadata such as `created_by` is kept).
5. **Read back:** compares the sha256 of the stored value with the minted token.
6. **Refresh:** runs `hokusai <env> refresh` in the app repo. This is a rolling restart; for `gravity` it restarts the core API, so do it off-peak.

You must type the env name before each mutating step, and `--dry-run` changes nothing. The token is never printed, logged or passed in argv. Rollback commands are printed at the end. A log with no secrets goes to `~/.local/state/rotate_app_trust_token/`.

## Requirements

- `vault`, `hokusai`, `python3`, `shasum`, `curl`.
- Local clones of `gravity` and the app (default `~/git/<name>`; override with `--gravity-dir` / `--app-dir`).
- The VPN for the target env, and a Vault identity that can write the secret. Setting `expires_at` also needs `kvv2/metadata` rights; without them the script asks before continuing and prints the command for someone who has them.
- A real terminal: `hokusai run` prints nothing without a tty.

## Usage

Do staging first:

```
S=src/rotate_app_trust_token/rotate.sh
$S --selftest                                                    # offline
$S --env staging --app pulse --key IMPULSE_JWT --dry-run         # read-only preview
$S --env staging --app pulse --key IMPULSE_JWT
$S --env production --app pulse --key IMPULSE_JWT --dry-run
$S --env production --app pulse --key IMPULSE_JWT
```

`--app` and `--key` are the project folder and key that the scan reports (e.g. `pulse` / `IMPULSE_JWT`).

After the refresh, check the app's logs for 401/403/JWT errors against the audience app. Then create a ticket for the next rotation, due a few weeks before the new `expires_at`.
