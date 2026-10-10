# Attack surface

| Route / asset | Method | Auth? | Input it accepts | Notes |
|---------------|--------|-------|------------------|-------|
| `/` | GET | no | none | home page |
| `/privacy/` | GET | no | none | static text |
| `/lang/<code>/` | GET | no | `fa` or `en` only | changes session language; redirect target is checked |
| `/order/` | POST | no | name, phone, email, plan, message, honeypot | CSRF token, 10 per IP per hour, 3 per phone per day |
| `/order/done/` | GET | session | none | shows the code stored in the visitor's own session |
| `/<ADMIN_URL>` | GET/POST | staff login | Django admin | lockout after 5 failures; path comes from env |
| `/static/*` | GET | no | none | served by Caddy, read-only volume |
| `/media/*` | GET | no | none | project screenshots (jpg/png/webp only), served by Caddy |

Not present: public API, file upload by visitors, webhooks, WebSockets, OAuth, payments.
Ports open on the server: 80 and 443 (Caddy). Postgres has no published port.