# Backups

- Service `backup` dumps the database and the media folder once a day.
- Files are encrypted with AES-256 (openssl) using `BACKUP_PASSPHRASE` from `.env.prod`.
  Keep that passphrase in the password manager. Without it the backups cannot be opened.
- Files live in the `backups_data` volume and are deleted after 14 days.

## Look at the backups

    docker compose --env-file .env.prod exec backup ls -lh /backups

## Test a restore (do this after setup and after every big change)

    docker compose --env-file .env.prod exec backup sh -c "tr -d '\r' < /scripts/restore_test.sh | sh"

It restores the newest backup into a temporary database, prints how many orders it found, and drops it.

## Restore for real (after a failure)

1. Stop the site: `docker compose --env-file .env.prod stop web cleaner`
2. Decrypt and load the chosen file into the database (on the server, Linux shell):

       openssl enc -d -aes-256-cbc -pbkdf2 -pass env:BACKUP_PASSPHRASE -in /backups/FILE.sql.gz.enc | gunzip | psql ...

3. Start the site again and re-apply any account deletions made since that backup.

## Off-site copy

The volume sits on the same server, so a dead server loses the backups too.
Once a week copy the newest encrypted files to another place (another server or a cloud drive).