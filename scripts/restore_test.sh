#!/bin/sh
set -eu

export PGPASSWORD="$POSTGRES_PASSWORD"
FILE=$(ls -1t /backups/studio141-db-*.sql.gz.enc | head -n 1)
echo "Testing restore from: $FILE"

psql -h db -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS restore_test;"
psql -h db -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE restore_test;"

openssl enc -d -aes-256-cbc -pbkdf2 -pass env:BACKUP_PASSPHRASE -in "$FILE" \
  | gunzip \
  | psql -q -h db -U "$POSTGRES_USER" -d restore_test -v ON_ERROR_STOP=1 > /dev/null

COUNT=$(psql -h db -U "$POSTGRES_USER" -d restore_test -tAc "select count(*) from orders_order;")
echo "Restore OK. Orders found in the restored copy: $COUNT"

psql -h db -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE restore_test;"