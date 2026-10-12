# Attack surface

| Route / asset | Method | Auth? | Input it accepts | Notes |
|---------------|--------|-------|------------------|-------|
| `/` | GET | no | `Accept-Language` header | redirects to `/fa/` or `/en/` |
| `/fa/`, `/en/` | GET | no | optional `?plan=<number>` (digits only, pre-selects a plan) | home page |
| `/fa/work/<slug>/`, `/en/work/<slug>/` | GET | no | slug (letters, digits, `-`, `_`) | project page; 404 for unpublished projects |
| `/fa/privacy/`, `/en/privacy/` | GET | no | none | static text |
| `/fa/order/`, `/en/order/` | POST (GET redirects home) | no | name, phone, email, plan, message, honeypot | CSRF token, 10 per IP per hour, 3 per phone per day |
| `/fa/order/done/`, `/en/order/done/` | GET | session | none | shows the code stored in the visitor's own session; `noindex` |
| `/sitemap.xml`, `/robots.txt` | GET | no | none | generated; robots.txt does not list the admin path |
| `/<ADMIN_URL>` | GET/POST | staff login + 2FA | Django admin | lockout after 5 failures; path comes from env; sends `X-Robots-Tag: noindex` |
| `/static/*` | GET | no | none | served by Caddy, read-only volume |
| `/media/*` | GET | no | none | project and team images (jpg/png/webp only, up to 2 MB), uploaded only by staff, served by Caddy |

Not present: public API, file upload by visitors, webhooks, WebSockets, OAuth, payments.
Ports open on the server: 80 and 443 (Caddy). Postgres has no published port.