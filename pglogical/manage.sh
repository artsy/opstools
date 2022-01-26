# automate some steps when migrating to new postgres instance using pglogical

function check_input() {
  if !(( $# == 4 ))
  then
    usage
    exit 1
  fi
}

function usage() {
  cat << EOF
    Usage: $0 olddb newdb action

    oldhost - old db host
    newhost - new db host
    db - name of db
    action - what to do
      datecheck - compare most recent updated_at between old/new dbs table by table.
      replstatus_old2new - check replication status of old->new.
      replstatus_new2old - check replication status of new->old.
      rowcount - compare row count table by table between old/new dbs.
      schemacheck - compare rails schema version between old/new dbs.
      sizecheck - compare table sizes between old/new dbs.
      adjust_newdb_seq - adjust sequences on new db - match old db plus an offset you specify.
EOF
}

function run_pg_cmd() {
  local HOST=$1
  local USER=$2
  local PASS=$3
  local DB=$4
  local CMD=$5

  local PG_URL="postgres://$USER:$PASS@$HOST:5432/$DB"
  docker run -u postgres --env PGCONNECT_TIMEOUT=5 postgres:"$PG_UTIL_VERSION"-alpine psql $PG_URL -c "$CMD"
}

function get_pass() {
  local PASS=''

  if [[ "$PGLOGICAL_PASS" == '' ]]
  then
    echo "Please provide $1 password:" > /dev/tty
    read -s PASS < /dev/tty
  else
    PASS="$PGLOGICAL_PASS"
  fi
  echo "$PASS"
}

function check_replication_status() {
  local PROVIDER=$1
  local SUBSCRIBER=$2
  local SUBSCRIPTION=$4

  local PG_CMD=''
  local PG_USER='pglogical'
  local TABLES=''

  local PASS=$(get_pass "$PG_USER")

  echo "Checking status of replication:"
  echo "from: $PROVIDER"
  echo "to: $SUBSCRIBER"

  echo
  echo "=== overall status ==="
  PG_CMD="SELECT subscription_name, status FROM pglogical.show_subscription_status();"
  run_pg_cmd "$SUBSCRIBER" "$PG_USER" "$PASS" "$DB" "$PG_CMD"

  PG_CMD='\dt public.*'
  TABLES=$(run_pg_cmd "$SUBSCRIBER" "$PG_USER" "$PASS" "$DB" "$PG_CMD")
  TABLES=$(echo "$TABLES" | grep -v 'List of relations' | grep -v '\-\-\-' | grep -v 'Schema' | awk '{print $3}')

  echo
  echo "=== per-table status ==="
  for table in $TABLES
  do
    PG_CMD="SELECT * FROM pglogical.show_subscription_table('$SUBSCRIPTION', '$table');"
    run_pg_cmd "$SUBSCRIBER" "$PG_USER" "$PASS" "$DB" "$PG_CMD"
  done
}

function check_schema() {
  local HOST=''
  local PG_USER='pglogical'
  local PG_CMD="SELECT * FROM schema_migrations ORDER BY version DESC LIMIT 1;"

  local PASS=$(get_pass "$PG_USER")
  
  HOST="$OLD_HOST"
  echo "$HOST $DB db schema version:"
  run_pg_cmd "$HOST" "$PG_USER" "$PASS" "$DB" "$PG_CMD"

  HOST="$NEW_HOST"
  echo "$HOST $DB db schema version:"
  run_pg_cmd "$HOST" "$PG_USER" "$PASS" "$DB" "$PG_CMD"
}

function compare_row_count() {
  local PG_USER='pglogical'
  local PG_CMD='\dt public.*'
  local PASS=$(get_pass "$PG_USER")
  local HOST=''

  TABLES=$(run_pg_cmd "$OLD_HOST" "$PG_USER" "$PASS" "$DB" "$PG_CMD")
  TABLES=$(echo "$TABLES" | grep -v 'List of relations' | grep -v '\-\-\-' | grep -v 'Schema' | awk '{print $3}')

  for table in $TABLES
  do
    echo "=== table: $table ==="
    PG_CMD="SELECT COUNT(*) FROM $table;"

    HOST="$OLD_HOST"
    echo "$HOST"
    run_pg_cmd "$HOST" "$PG_USER" "$PASS" "$DB" "$PG_CMD"

    HOST="$NEW_HOST"
    echo "$HOST"
    run_pg_cmd "$HOST" "$PG_USER" "$PASS" "$DB" "$PG_CMD"
  done
}

function compare_table_sizes() {
  local PG_USER='pglogical'
  local PG_CMD='\dt public.*'
  local PASS=$(get_pass "$PG_USER")
  local HOST=''

  TABLES=$(run_pg_cmd "$OLD_HOST" "$PG_USER" "$PASS" "$DB" "$PG_CMD")
  TABLES=$(echo "$TABLES" | grep -v 'List of relations' | grep -v '\-\-\-' | grep -v 'Schema' | awk '{print $3}')

  for table in $TABLES
  do
    echo "=== table: $table ==="
    PG_CMD="
      SELECT schemaname,relname,pg_size_pretty(pg_relation_size(relid))
      FROM pg_catalog.pg_statio_user_tables
      WHERE schemaname='public' AND relname='$table';
    "

    HOST="$OLD_HOST"
    echo "$HOST"
    run_pg_cmd "$HOST" "$PG_USER" "$PASS" "$DB" "$PG_CMD"

    HOST="$NEW_HOST"
    echo "$HOST"
    run_pg_cmd "$HOST" "$PG_USER" "$PASS" "$DB" "$PG_CMD"

  done
}

function compare_updated_at() {
  local PG_USER='pglogical'
  local PG_CMD='\dt public.*'
  local PASS=$(get_pass "$PG_USER")
  local HOST=''

  TABLES=$(run_pg_cmd "$OLD_HOST" "$PG_USER" "$PASS" "$DB" "$PG_CMD")
  TABLES=$(echo "$TABLES" | grep -v 'List of relations' | grep -v '\-\-\-' | grep -v 'Schema' | awk '{print $3}')

  for table in $TABLES
  do
    echo "=== table: $table ==="
    PG_CMD="SELECT updated_at FROM $table ORDER BY updated_at DESC LIMIT 1;"

    HOST="$OLD_HOST"
    echo "$HOST"
    run_pg_cmd "$HOST" "$PG_USER" "$PASS" "$DB" "$PG_CMD"

    HOST="$NEW_HOST"
    echo "$HOST"
    run_pg_cmd "$HOST" "$PG_USER" "$PASS" "$DB" "$PG_CMD"
  done
}

function adjust_sequences() {
  local SRC_HOST=$1
  local DST_HOST=$2
  local PG_USER=''
  local PG_CMD=''
  local OFFSET=0
  local SEQVAL=''
  local DUMMY=''

  echo "Sync sequence values from $SRC_HOST to $DST_HOST plus offset."

  echo "Enter DB user: "
  read PG_USER < /dev/tty
  local PASS=$(get_pass "$PG_USER")

  echo "Enter offset:"
  read OFFSET < /dev/tty

  PG_CMD='\ds public.*'
  SEQS=$(run_pg_cmd "$SRC_HOST" "$PG_USER" "$PASS" "$DB" "$PG_CMD")
  SEQS=$(echo "$SEQS" | grep -v 'List of relations' | grep -v '\-\-\-' | grep -v 'Schema' | awk '{print $3}')

  for seq in $SEQS
  do
    SEQVAL=''

    PG_CMD="SELECT last_value FROM $seq;"

    echo "=== sequence: $seq ==="
    HOST="$SRC_HOST"
    echo "$HOST last value:"
    DUMMY=$(run_pg_cmd "$HOST" "$PG_USER" "$PASS" "$DB" "$PG_CMD")
    echo "$DUMMY"
    SEQVAL=$(echo "$DUMMY" | grep -v 'last_value' | grep -v 'row' | grep -v '\-\-\-' | awk '{print $1}')

    HOST="$DST_HOST"
    echo "$HOST last value:"
    run_pg_cmd "$HOST" "$PG_USER" "$PASS" "$DB" "$PG_CMD"

    HOST="$DST_HOST"
    SEQVAL=$(( $SEQVAL + $OFFSET ))
    read -p "Do you want to set seq value to $SEQVAL on $DST_HOST?" < /dev/tty
    PG_CMD="SELECT setval('$seq', $SEQVAL, false);"
    run_pg_cmd "$HOST" "$PG_USER" "$PASS" "$DB" "$PG_CMD"
    PG_CMD="SELECT last_value FROM $seq;"
    run_pg_cmd "$HOST" "$PG_USER" "$PASS" "$DB" "$PG_CMD"
  done
}

check_input "$@"

OLD_HOST=$1
NEW_HOST=$2
DB=$3
ACTION=$4

PG_UTIL_VERSION='<new-pg-version>'

case "$ACTION" in
  'datecheck')
    compare_updated_at
    ;;
  'replstatus_old2new')
    check_replication_status "$OLD_HOST" "$NEW_HOST" "$DB" 'old2new'
    ;;
  'replstatus_new2old')
    check_replication_status "$NEW_HOST" "$OLD_HOST" "$DB" 'new2old'
    ;;
  'rowcount')
    compare_row_count
    ;;
  'schemacheck')
    check_schema
    ;;
  'sizecheck')
    compare_table_sizes
    ;;
  'adjust_newdb_seq')
    adjust_sequences $OLD_HOST $NEW_HOST
    ;;
  *)
    usage
    ;;
esac
