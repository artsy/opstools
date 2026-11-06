#!/usr/bin/env bash
# Rotate an Artsy App Trust token (a JWT minted by Gravity) stored in Vault at kvv2/kubernetes/apps/<app>/<KEY>.
# Use it when the weekly vault JWT expiration scan (src/list_vault_jwt_expiration) flags a token. See README.md.
# Playbook: Notion "Engineering Playbooks" > "How to rotate an App Trust Token" (+ "Hashicorp Vault (developer instructions)").
#
# Run by hand in a real terminal (hokusai run needs a tty), on the VPN of the target env. Staging first:
#   S=src/rotate_app_trust_token/rotate.sh
#   $S --selftest                                                # offline, no side effects
#   $S --env staging --app pulse --key IMPULSE_JWT --dry-run     # read-only: current token, expiry, derived ids, plan
#   $S --env staging --app pulse --key IMPULSE_JWT               # real run
#   $S --env production --app pulse --key IMPULSE_JWT --dry-run && $S --env production --app pulse --key IMPULSE_JWT
# Options: --gravity-dir DIR (where tokens are minted, default ~/git/gravity)
#          --app-dir DIR     (where `hokusai <env> refresh` runs, default ~/git/<app>)
#
# Flow: preflight (read-only) -> mint in Gravity <env> -> verify -> write to Vault (+ expires_at metadata if permitted)
#       -> read-back -> `hokusai <env> refresh` in the app repo.
# Audience and subject ids are NOT typed: they are read from the claims of the CURRENT token (aud, subject_application),
# shown to you, and the new token must carry identical non-time claims.
# Safety: one Vault per --env (refuses any other VAULT_ADDR); token never printed/logged/in argv; each mutation needs you
#         to type the env name; --dry-run mutates nothing. Rollback commands are printed at the end and logged.
# WARNING: the refresh is a rolling restart of the app in that env (--app gravity = the core API: off-peak, team told).
#
# Shortcuts: no post-refresh health probe (manual check printed at the end); claim names are not assumed beyond
#            aud/subject_application; expires_at is skipped when your Vault identity lacks metadata rights.
set -euo pipefail
set +x # never trace: variables hold the token

# ---------- config ----------
MOUNT="kvv2"
EXPIRES_IN_SECONDS=31557600 # 1 year, per playbook
GRAVITY_DIR="${GRAVITY_DIR:-$HOME/git/gravity}"
LOG_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/rotate_app_trust_token" # outside the repo: never committed

ENV="" APP="" SECRET_KEY="" APP_DIR="" DRY_RUN=0 SELFTEST=0
STATE="preflight" # preflight | minted | vault-written | refreshed
OLD_VERSION="" OLD_EXPIRES="" NEW_TOKEN="" OLD_TOKEN="" AUD="" SUB="" LOG=""

# ---------- output helpers ----------
if [[ -t 1 ]]; then B=$'\e[1m' G=$'\e[32m' R=$'\e[31m' Y=$'\e[33m' D=$'\e[2m' N=$'\e[0m'; else B="" G="" R="" Y="" D="" N=""; fi
JWT_RE='eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*'
redact() { sed -E "s/$JWT_RE/<jwt-redacted>/g"; }
plain() { printf '%s\n' "$*" | sed -E $'s/\e\\[[0-9;]*m//g'; }
log() { [[ -n "$LOG" ]] && plain "$(date -u +%FT%TZ) $*" >>"$LOG"; return 0; }
step() { printf '\n%s== %s ==%s\n' "$B" "$*" "$N"; log "STEP $*"; }
ok() { printf '  %s✔%s %s\n' "$G" "$N" "$*"; log "ok: $*"; }
info() { printf '  %s·%s %s\n' "$D" "$N" "$*"; log "info: $*"; }
warn() { printf '  %s!%s %s\n' "$Y" "$N" "$*"; log "warn: $*"; }
die() { printf '  %s✘ %s%s\n' "$R" "$*" "$N" >&2; log "FAIL: $*"; exit 1; }
confirm() { # $1 prompt; must type the env name (a reflex "yes" is not enough)
  local a
  read -r -p "  ${B}$1${N} Type '$ENV' to continue: " a
  [[ "$a" == "$ENV" ]] || die "Aborted by user at: $1"
}
pyj() { python3 -I -c 'import sys,json;d=json.load(sys.stdin);print(eval(sys.argv[1]))' "$1"; } # JSON on stdin, fixed expressions only
secret_path() { printf 'kubernetes/apps/%s/%s' "$1" "$2"; } # same layout opstools-vault-jwt-scan walks

# ---------- JWT helpers (token on stdin, never argv) ----------
jwt_claims() {
  python3 -I -c '
import sys, json, base64
t = sys.stdin.read().strip()
parts = t.split(".")
if len(parts) != 3: sys.exit("not a JWT")
p = parts[1]; p += "=" * (-len(p) % 4)
print(json.dumps(json.loads(base64.urlsafe_b64decode(p)), sort_keys=True))'
}
claims_fingerprint() { # claims JSON on stdin -> JSON without per-token time/id claims
  python3 -I -c '
import sys, json
d = json.load(sys.stdin)
for k in ("iat", "exp", "nbf", "jti"): d.pop(k, None)
print(json.dumps(d, sort_keys=True))'
}
iso_from_epoch() { python3 -I -c 'import sys,datetime;print(datetime.datetime.fromtimestamp(int(sys.argv[1]),datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))' "$1"; }
sha() { printf '%s' "$1" | shasum -a 256 | cut -d' ' -f1; }

# ---------- selftest (offline) ----------
selftest() {
  local fails=0 t claims
  chk() { if [[ "$2" == "$3" ]]; then ok "$1"; else printf '  %s✘ %s: got [%s] want [%s]%s\n' "$R" "$1" "$2" "$3" "$N"; fails=$((fails + 1)); fi; }
  t="eyJhbGciOiJIUzI1NiJ9.$(printf '{"aud":"A1","exp":1800000000,"iat":1700000000,"subject_application":"S1"}' | base64 | tr '+/' '-_' | tr -d '=\n').c2ln"
  claims="$(printf '%s' "$t" | jwt_claims)"
  chk "jwt_claims decodes payload" "$claims" '{"aud": "A1", "exp": 1800000000, "iat": 1700000000, "subject_application": "S1"}'
  chk "aud/subject_application extraction" "$(printf '%s' "$claims" | pyj 'd["aud"]+"/"+d["subject_application"]')" "A1/S1"
  chk "claims_fingerprint drops time claims" "$(printf '%s' "$claims" | claims_fingerprint)" '{"aud": "A1", "subject_application": "S1"}'
  chk "iso_from_epoch" "$(iso_from_epoch 1800000000)" "2027-01-15T08:00:00Z"
  chk "redact hides token, keeps text" "$(printf 'pod x %s deleted' "$t" | redact)" "pod x <jwt-redacted> deleted"
  chk "secret_path layout" "$(secret_path pulse IMPULSE_JWT)" "kubernetes/apps/pulse/IMPULSE_JWT"
  [[ $fails -eq 0 ]] || die "$fails selftest check(s) failed"
  printf '\n%sselftest passed%s\n' "$G" "$N"
}

# ---------- args ----------
usage() { awk 'NR>1 { if (/^#/) { sub(/^# ?/, ""); print } else exit }' "${BASH_SOURCE[0]}"; exit "${1:-0}"; }
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) ENV="${2:-}"; shift 2 ;;
    --app) APP="${2:-}"; shift 2 ;;
    --key) SECRET_KEY="${2:-}"; shift 2 ;;
    --gravity-dir) GRAVITY_DIR="${2:-}"; shift 2 ;;
    --app-dir) APP_DIR="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --selftest) SELFTEST=1; shift ;;
    -h | --help) usage 0 ;;
    *) printf 'unknown arg: %s\n' "$1" >&2; usage 1 ;;
  esac
done

if [[ $SELFTEST -eq 1 ]]; then step "Selftest (offline)"; selftest; exit 0; fi

case "$ENV" in
  staging) VAULT_ADDR_EXPECTED="https://vault.stg.artsy.systems:8200" ;;
  production) VAULT_ADDR_EXPECTED="https://vault.prd.artsy.systems:8200" ;;
  *) die "--env staging|production is required (no default, on purpose)" ;;
esac
# Names go into a Vault path, a log file name and a rake arg list: keep them to plain identifiers.
[[ "$APP" =~ ^[a-z0-9][a-z0-9_-]*$ ]] || die "--app <app> is required (lowercase Vault folder under kubernetes/apps, e.g. pulse)"
[[ "$SECRET_KEY" =~ ^[A-Za-z0-9_]+$ ]] || die "--key <KEY> is required (the secret/env var name, e.g. IMPULSE_JWT)"
APP_DIR="${APP_DIR:-$HOME/git/$APP}"
SECRET_PATH="$(secret_path "$APP" "$SECRET_KEY")"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/rotate-$APP-$SECRET_KEY-$ENV.log"
: >>"$LOG" && chmod 600 "$LOG"

trap 'rc=$?; [[ $rc -ne 0 ]] && {
  printf "\n%sStopped in state: %s%s\n" "$R" "$STATE" "$N"
  case "$STATE" in
    minted) printf "Nothing written to Vault yet. Safe to re-run.\n" ;;
    vault-written) printf "Vault already has the NEW token but pods may not have it. Either re-run only: (cd %s && hokusai %s refresh), or roll back (see log: %s).\n" "$APP_DIR" "$ENV" "$LOG" ;;
  esac; log "exit $rc in state $STATE"; }' EXIT

# ---------- 1. preflight ----------
step "1/6 Preflight (read-only) - $ENV, $APP/$SECRET_KEY"
for c in vault hokusai python3 shasum curl; do command -v "$c" >/dev/null || die "missing tool: $c"; done
ok "tools present: vault hokusai python3 shasum curl"

if [[ -n "${VAULT_ADDR:-}" && "$VAULT_ADDR" != "$VAULT_ADDR_EXPECTED" ]]; then
  die "VAULT_ADDR is '$VAULT_ADDR' but --env $ENV needs $VAULT_ADDR_EXPECTED. Unset it and retry."
fi
export VAULT_ADDR="$VAULT_ADDR_EXPECTED"
ok "VAULT_ADDR = $ENV ($VAULT_ADDR)"

for d in "$GRAVITY_DIR" "$APP_DIR"; do
  [[ -f "$d/hokusai/$ENV.yml" ]] || die "$d has no hokusai/$ENV.yml (set --gravity-dir / --app-dir)"
done
ok "hokusai projects found: mint in $GRAVITY_DIR, refresh in $APP_DIR"

code="$(curl -sk --max-time 8 -o /dev/null -w '%{http_code}' "$VAULT_ADDR/v1/sys/health" || true)"
[[ "$code" =~ ^(200|429|472|473)$ ]] || die "Vault $ENV unreachable (HTTP '${code:-none}'). Connect to the $ENV VPN."
ok "Vault $ENV reachable (HTTP $code)"

if ! vault token lookup >/dev/null 2>&1; then
  warn "no valid Vault token, logging in (IAM user, default profile; roles are unsupported)"
  AWS_PROFILE=default vault login -method=aws >/dev/null || die "vault login failed"
fi
vault token lookup >/dev/null 2>&1 || die "still no valid Vault token"
ok "Vault token valid for $ENV"

caps="$(vault token capabilities "$MOUNT/data/$SECRET_PATH" 2>/dev/null || true)"
[[ "$caps" == *patch* || "$caps" == *update* ]] || die "Vault identity cannot write $MOUNT/data/$SECRET_PATH (capabilities: ${caps:-none})"
ok "can write the secret (capabilities: $caps)"

cur_json="$(vault kv get -format=json -mount "$MOUNT" "$SECRET_PATH")" || die "cannot read $MOUNT/$SECRET_PATH (policy? wrong path?)"
OLD_TOKEN="$(printf '%s' "$cur_json" | pyj 'd["data"]["data"]["'"$SECRET_KEY"'"]')" || die "$SECRET_KEY key missing in secret"
OLD_VERSION="$(printf '%s' "$cur_json" | pyj 'd["data"]["metadata"]["version"]')"
other_keys="$(printf '%s' "$cur_json" | pyj 'sorted(k for k in d["data"]["data"] if k != "'"$SECRET_KEY"'")')"
ok "read current secret (version $OLD_VERSION); other keys in secret: $other_keys (preserved via kv patch)"

old_claims="$(printf '%s' "$OLD_TOKEN" | jwt_claims)" || die "current value is not a decodable JWT"
old_fp="$(printf '%s' "$old_claims" | claims_fingerprint)"
AUD="$(printf '%s' "$old_claims" | pyj 'd.get("aud","")')"
SUB="$(printf '%s' "$old_claims" | pyj 'd.get("subject_application","")')"
[[ "$AUD" =~ ^[A-Za-z0-9_-]+$ ]] || die "current token has no usable aud claim"
[[ "$SUB" =~ ^[A-Za-z0-9_-]+$ ]] || die "current token has no usable subject_application claim"
[[ "$AUD" != "$SUB" ]] || warn "aud and subject_application are identical: the current token is self-referential. The new token must match it exactly, which step 3 enforces."
ok "ids derived from the current token: audience=$AUD subject=$SUB"
info "current token claims (non-secret): $old_claims"

old_exp="$(printf '%s' "$old_claims" | pyj 'd.get("exp","")')"
if [[ -n "$old_exp" ]]; then
  OLD_EXPIRES="$(iso_from_epoch "$old_exp")"
  left=$(( old_exp - $(date +%s) ))
  if [[ $left -le 0 ]]; then warn "current token ALREADY EXPIRED at $OLD_EXPIRES"; else info "current token expires $OLD_EXPIRES (in $((left / 3600))h)"; fi
else
  warn "current token has no exp claim"
fi

META_OK=1
if meta_json="$(vault kv metadata get -format=json -mount "$MOUNT" "$SECRET_PATH" 2>/dev/null)"; then
  info "current custom_metadata: $(printf '%s' "$meta_json" | pyj 'd["data"].get("custom_metadata")')"
else
  META_OK=0
  warn "cannot read secret metadata (403). expires_at cannot be set by this identity."
fi
log "previous: env=$ENV app=$APP key=$SECRET_KEY version=$OLD_VERSION expires=$OLD_EXPIRES"

if [[ $DRY_RUN -eq 1 ]]; then
  step "Dry run complete. Would do:"
  info "2. mint token:  (cd $GRAVITY_DIR && hokusai $ENV run 'bundle exec rake token[$AUD,$SUB,$EXPIRES_IN_SECONDS]')"
  info "3. verify it decodes, differs from current, has identical non-time claims, exp ~1y out"
  info "4. vault kv patch $MOUNT/$SECRET_PATH$([[ $META_OK -eq 1 ]] && echo ' + vault kv metadata patch expires_at (other keys kept)' || echo ' (metadata skipped: no permission)')"
  info "5. read back and compare sha256"
  info "6. (cd $APP_DIR && hokusai $ENV refresh)   # rolling restart of $APP $ENV"
  exit 0
fi

if [[ $META_OK -eq 0 ]]; then
  warn "Rotation can still proceed: the secret itself is writable. expires_at must then be set by someone with metadata rights (command printed at the end). Until then the weekly opstools scan keeps using the OLD date."
  confirm "Continue WITHOUT setting expires_at metadata?"
fi

# ---------- 2. mint ----------
step "2/6 Mint new token in Gravity $ENV"
confirm "Mint a new $ENV App Trust token for $APP/$SECRET_KEY (audience=$AUD, subject=$SUB, 1 year)?"
raw="$(cd "$GRAVITY_DIR" && hokusai "$ENV" run "bundle exec rake token[$AUD,$SUB,$EXPIRES_IN_SECONDS]" 2>&1)" \
  || { printf '%s\n' "$raw" | redact | tail -20; die "hokusai run failed (output above, tokens redacted)"; }
NEW_TOKEN="$(printf '%s\n' "$raw" | grep -oE "$JWT_RE" | tail -1 || true)"
unset raw
[[ -n "$NEW_TOKEN" ]] || die "no JWT found in hokusai output (empty output: run from a real terminal; else is the ClientApplication id valid?)"
STATE="minted"
ok "token minted (not displayed)"

# ---------- 3. verify minted token ----------
step "3/6 Verify the new token before it touches Vault"
new_claims="$(printf '%s' "$NEW_TOKEN" | jwt_claims)" || die "new token does not decode"
[[ "$NEW_TOKEN" != "$OLD_TOKEN" ]] || die "new token is identical to the current one"
ok "decodes, and differs from the current token"
if [[ "$(printf '%s' "$new_claims" | claims_fingerprint)" == "$old_fp" ]]; then
  ok "identical audience/subject/roles (all non-time claims match the current token)"
else
  warn "non-time claims differ from the current token:"
  info "old: $old_fp"
  info "new: $(printf '%s' "$new_claims" | claims_fingerprint)"
  confirm "Claims differ on $ENV. Continue anyway?"
fi
new_exp="$(printf '%s' "$new_claims" | pyj 'd.get("exp","")')"
want=$(( $(date +%s) + EXPIRES_IN_SECONDS ))
if [[ -n "$new_exp" ]]; then
  drift=$(( new_exp > want ? new_exp - want : want - new_exp ))
  [[ $drift -lt 86400 ]] || die "exp claim is $((drift / 86400)) days off the requested 1 year"
  NEW_EXPIRES="$(iso_from_epoch "$new_exp")"
  ok "expires $NEW_EXPIRES (~1 year)"
else
  NEW_EXPIRES="$(iso_from_epoch "$want")"
  warn "no exp claim; using requested lifetime for metadata: $NEW_EXPIRES"
fi

# ---------- 4. vault ----------
step "4/6 Write to Vault $ENV"
confirm "Write new $SECRET_KEY to $MOUNT/$SECRET_PATH (current v$OLD_VERSION becomes the rollback point)?"
printf '%s' "$NEW_TOKEN" | vault kv patch -mount "$MOUNT" "$SECRET_PATH" "$SECRET_KEY=-" >/dev/null || die "vault kv patch failed"
STATE="vault-written"
ok "secret updated"
if [[ $META_OK -eq 1 ]]; then
  # patch (not put) merges custom_metadata, so created_by etc. are kept
  vault kv metadata patch -mount "$MOUNT" -custom-metadata "expires_at=$NEW_EXPIRES" "$SECRET_PATH" >/dev/null \
    || die "metadata update failed (secret IS updated; set expires_at by hand)"
  ok "custom_metadata expires_at=$NEW_EXPIRES"
else
  warn "skipped expires_at metadata (no permission); see the command at the end"
fi

# ---------- 5. read back ----------
step "5/6 Read back from Vault"
back_json="$(vault kv get -format=json -mount "$MOUNT" "$SECRET_PATH")"
back_token="$(printf '%s' "$back_json" | pyj 'd["data"]["data"]["'"$SECRET_KEY"'"]')"
[[ "$(sha "$back_token")" == "$(sha "$NEW_TOKEN")" ]] || die "Vault value does not match the minted token (sha256 mismatch)"
ok "Vault value matches minted token (sha256 compared)"
new_ver="$(printf '%s' "$back_json" | pyj 'd["data"]["metadata"]["version"]')"
[[ "$new_ver" == "$((OLD_VERSION + 1))" ]] || warn "version is $new_ver, expected $((OLD_VERSION + 1)) (someone else wrote concurrently?)"
if [[ $META_OK -eq 1 ]]; then
  back_meta_json="$(vault kv metadata get -format=json -mount "$MOUNT" "$SECRET_PATH")"
  back_meta="$(printf '%s' "$back_meta_json" | pyj 'd["data"]["custom_metadata"]')"
  back_exp="$(printf '%s' "$back_meta_json" | pyj 'd["data"]["custom_metadata"].get("expires_at")')"
  [[ "$back_exp" == "$NEW_EXPIRES" ]] || die "metadata expires_at is '$back_exp', expected '$NEW_EXPIRES'"
  ok "version $new_ver, custom_metadata=$back_meta"
else
  ok "version $new_ver (metadata not checked)"
fi
unset back_token

# ---------- 6. refresh ----------
step "6/6 Refresh $APP $ENV so pods pick up the new token"
warn "This is a rolling restart of $APP $ENV$([[ "$APP" == gravity ]] && echo ' (core API). Off-peak only.')"
confirm "Run 'hokusai $ENV refresh' in $APP_DIR?"
(cd "$APP_DIR" && hokusai "$ENV" refresh) || die "hokusai refresh failed (Vault is updated; retry the refresh by hand)"
STATE="refreshed"
ok "refresh issued"
unset NEW_TOKEN OLD_TOKEN

# ---------- done ----------
step "Done: $APP/$SECRET_KEY rotated in $ENV"
printf '  Next, by hand:\n'
printf '   1. Verify %s still talks to the audience app (no 401/403/JWT errors): (cd %s && hokusai %s logs -t 400 -s)\n' "$APP" "$APP_DIR" "$ENV"
printf '   2. If broken, roll back:\n'
printf '        export VAULT_ADDR=%s\n' "$VAULT_ADDR_EXPECTED"
printf '        vault kv rollback -mount %s -version=%s %s\n' "$MOUNT" "$OLD_VERSION" "$SECRET_PATH"
printf '        vault kv metadata patch -mount %s -custom-metadata expires_at=%s %s\n' "$MOUNT" "${OLD_EXPIRES:-<old>}" "$SECRET_PATH"
printf '        (cd %s && hokusai %s refresh)\n' "$APP_DIR" "$ENV"
if [[ $META_OK -eq 0 ]]; then
  printf '   ! expires_at NOT set (no metadata permission). Someone with metadata rights runs:\n'
  printf '        export VAULT_ADDR=%s\n' "$VAULT_ADDR_EXPECTED"
  printf '        vault kv metadata patch -mount %s -custom-metadata expires_at=%s %s\n' "$MOUNT" "$NEW_EXPIRES" "$SECRET_PATH"
  log "TODO: set expires_at=$NEW_EXPIRES on $MOUNT/$SECRET_PATH (metadata permission missing)"
fi
printf '   3. Then: the other env (--env %s), and a ticket due ~%s for next year'"'"'s rotation.\n' "$([[ "$ENV" == staging ]] && echo production || echo staging)" "${NEW_EXPIRES%%T*}"
printf '   Log (no secrets): %s\n' "$LOG"
log "DONE $ENV $APP/$SECRET_KEY: v$OLD_VERSION -> v$new_ver, expires $NEW_EXPIRES. rollback: vault kv rollback -mount $MOUNT -version=$OLD_VERSION $SECRET_PATH"
