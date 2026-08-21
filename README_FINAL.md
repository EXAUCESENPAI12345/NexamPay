# NexamPay Backend — Final Build

## Architecture

- FastAPI + SQLAlchemy async
- PostgreSQL in production
- Telegram Mini App authentication
- NexamPay public ID format: `NXP-XXXXXXXX`
- Wallet / deposits / transfers / withdrawals
- Mobile Money provider-ready webhooks
- Shop / orders / revenue ledger
- Admin access restricted by `ADMIN_TELEGRAM_ID`
- Virtual card application + administrator approval

## Virtual card policy

NexamPay does **not** request an identity card, passport, national ID or other identity-document upload for the virtual-card application in this build.

The user submits only the information required by the product flow:
- country
- cardholder name
- phone number

The application remains `pending` until an administrator reviews it.

Admin endpoints:
- `GET /api/v1/admin/cards/applications`
- `POST /api/v1/admin/cards/applications/{application_id}/approve`
- `POST /api/v1/admin/cards/applications/{application_id}/reject`

User endpoints:
- `POST /api/v1/cards/applications`
- `GET /api/v1/cards/application`
- `GET /api/v1/cards/me`
- `POST /api/v1/cards/{card_id}/freeze`
- `POST /api/v1/cards/{card_id}/unfreeze`

### Important card limitation

The backend never invents or stores a real PAN/CVV. A real payment card must be issued by a compatible card provider. The virtual-card model is provider-ready and stores only safe display/provider references such as `masked_number`, `last4`, expiry metadata and `provider_card_id`.

## Migrations

The repository contains the complete Alembic history, including the virtual-card
branch. The current final head is:

```text
0016_user_network_and_settings
```

Run:

```bash
alembic upgrade head
```

The final migration also adds the account PIN hash field and merges the historical
migration branches.

## Fees

Current configured deposit/withdrawal policy:
- up to 1,500 FCFA: 0 fee
- above 1,500 FCFA: 5%

Internal transfer fee: 3% on every transfer.

## Deployment

Do not commit `.env` or real Telegram/provider secrets.

Production values belong in Render environment variables.

### Telegram bot

The bot worker is `bot.py`. Run it as a separate background worker/process so FastAPI remains the API service. The bot handles `/start` and the administrator-only `/announce` (also `/annonce`) command.
