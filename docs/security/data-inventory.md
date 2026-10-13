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
| form security cookie (CSRF) | protects the order form | browser cookie | the visitor, the app | Secure in production | until the browser session ends |
| session cookie | shows the tracking code after sending a request; admin login | browser cookie + `django_session` | the visitor, the app | HttpOnly, Secure in production | 30 minutes idle |
| backups | restore after a failure | `backups_data` volume (encrypted files) | whoever has server access and the backup passphrase | AES-256 (openssl) | 14 days |
| copy of each request in the team's Telegram chat | to see new requests quickly | Telegram (private chats of team members) | those team members | Telegram's own transport encryption (not end-to-end) | 12 months (deleted by hand) |
| copy of each request in the team email (optional) | same | the team mailbox | whoever can open the mailbox | provider's encryption | 12 months (deleted by hand) |

The site language is in the URL (`/fa/`, `/en/`) and needs no cookie.

Not collected: card data, national ID, address, location, analytics.

## Third parties that receive visitor data

- **Fonts**: served from the site itself. No third party sees the visit.
- **Contact buttons and cards** (Telegram, email, WhatsApp, Instagram): plain links. Nothing is sent to these services until the visitor clicks.
- **Telegram** (new-order notification to the team's bot): with `TELEGRAM_FULL_DETAILS=True` (the default) it gets the whole form: code, name, phone, email, plan, message, time and language. The chats must be private chats of team members only. With `False` it gets only the code, plan and a masked phone.
- **Email provider** (only if `EMAIL_HOST` and `ORDER_NOTIFY_EMAIL_TO` are set): gets the same content as the Telegram message, as plain text.

## Retention

The 12 months is a default and needs the owner's decision. Deletion in the database runs automatically every day
(`purge_orders --days 365` and `clearsessions`, service `cleaner` in `docker-compose.yml`).
Backups older than 14 days are deleted by the `backup` service. Note: a deleted order stays in backups for up to 14 more days.

The copies in Telegram and email are NOT deleted automatically. One team member has to clear messages older than 12 months by hand,
because the privacy page promises it.