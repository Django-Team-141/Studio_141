#!/bin/sh
set -eu

export PGPASSWORD="$POSTGRES_PASSWORD"
mkdir -p /backups

while true; do
  STAMP=$(date +%Y%m%d-%H%M%S)

  pg_dump -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /tmp/dump.sql
  gzip -c /tmp/dump.sql | openssl enc -aes-256-cbc -pbkdf2 -salt \
    -pass env:BACKUP_PASSPHRASE -out "/backups/studio141-db-$STAMP.sql.gz.enc.tmp"
  rm -f /tmp/dump.sql
  mv "/backups/studio141-db-$STAMP.sql.gz.enc.tmp" "/backups/studio141-db-$STAMP.sql.gz.enc"

  tar -czf - -C /media . | openssl enc -aes-256-cbc -pbkdf2 -salt \
    -pass env:BACKUP_PASSPHRASE -out "/backups/studio141-media-$STAMP.tar.gz.enc"

  # بکاپ‌های قدیمی‌تر از ۱۴ روز پاک می‌شوند
  find /backups -name 'studio141-*.enc' -mtime +14 -delete

  echo "backup done: $STAMP"
  sleep 86400
done