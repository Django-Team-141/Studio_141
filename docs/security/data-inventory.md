# Data inventory

What the site stores about visitors, why, and for how long.

| Field | Why we need it | Where it lives | Who can read it | Encrypted? | Kept until |
|-------|----------------|----------------|-----------------|------------|------------|
| name | to address the person when we call | `orders_order.name` | team (admin panel, 2FA) | in transit (HTTPS), disk encryption on the host, encrypted backups | 12 months after the request |
| phone | to call the person back | `orders_order.phone` | team (admin panel, masked in the list) | same | 12 months |
| email (optional) | optional second way to reach them | `orders_order.email` | team | same | 12 months |
| message | project details they wrote | `orders_order.message` | team | same | 12 months |
| chosen plan | to know what they asked about | `orders_order.plan` | team | same | 12 months |
| language | to answer in the same language | `orders_order.lang` | team | same | 12 months |
| session cookie | remembers the language, protects the form | browser cookie + `django_session` | the visitor, the app | HttpOnly, Secure in production | 30 minutes idle |
| backups | restore after a failure | `backups_data` volume (encrypted files) | whoever has server access and the backup passphrase | AES-256 (openssl) | 14 days |

Not collected: card data, national ID, address, location, analytics.

## Third parties that receive visitor data

- **Google Fonts**: the visitor's browser requests the fonts directly. No form data is sent.
- **Telegram** (new-order notification to the team's bot):
  - default (`TELEGRAM_FULL_DETAILS=False`): request code, plan, language, masked phone (like `0912***567`). No name, no message.
  - if `TELEGRAM_FULL_DETAILS=True`: also name, full phone, email and the first 300 characters of the message. Turning this on is a conscious choice by the owner; the privacy page says so.

## Retention

The 12 months is a default and needs the owner's decision. Deletion runs automatically every day
(`purge_orders --days 365` and `clearsessions`, service `cleaner` in `docker-compose.yml`).
Backups older than 14 days are deleted by the `backup` service. Note: a deleted order stays in backups for up to 14 more days.