# NexamPay Frontend API Contract

Base URL:
`https://<your-render-service>/api/v1`

Authentication:
`Authorization: Bearer <session_token>`

## Core

- `POST /auth/telegram`
- `POST /auth/telegram/create-account` — body: `init_data`, `country_id`, `pin`, optional `network_id`
- `POST /auth/logout`
- `GET /profile`
- `GET /wallet`
- `GET /transactions`
- `GET /history`
- `GET /notifications`
- `GET /countries`
- `GET /mobile-money/networks/{country_id}` (available before account creation)
- `GET /settings`
- `PATCH /settings` — language, currency_code, color, theme, bot_notifications_enabled

## Money

- `POST /deposits`
- `POST /withdrawals`
- `POST /transfers/preview`
- `POST /transfers/confirm`

## Shop

- `GET /shop/categories`
- `GET /shop/products`
- `POST /orders`

## Virtual card

- `POST /cards/applications`
- `GET /cards/application`
- `GET /cards/me`
- `POST /cards/{card_id}/freeze`
- `POST /cards/{card_id}/unfreeze`

Admin:
- `GET /admin/cards/applications`
- `POST /admin/cards/applications/{application_id}/approve`
- `POST /admin/cards/applications/{application_id}/reject`


## Admin

All admin routes require the normal Bearer session token and an account whose
Telegram ID equals `ADMIN_TELEGRAM_ID`.

- `GET /admin/session`
- `GET /admin/stats`
- `GET /admin/deposits`
- `POST /admin/deposits/{deposit_id}/approve`
- `POST /admin/deposits/{deposit_id}/reject`
- `GET /admin/withdrawals`
- `POST /admin/withdrawals/{withdrawal_id}/approve`
- `POST /admin/withdrawals/{withdrawal_id}/reject`
- `GET /admin/transfers`
- `GET /admin/shop/categories`
- `GET /admin/shop/products`
- `POST /admin/shop/categories`
- `POST /admin/shop/products`
- `PATCH /admin/shop/products/{product_id}`
- `GET /admin/orders`
- `POST /admin/orders/{order_number}/approve`
- `POST /admin/orders/{order_number}/reject`
- `GET /admin/revenue`
- `GET /admin/cards/applications`
- `POST /admin/cards/applications/{application_id}/approve`
- `POST /admin/cards/applications/{application_id}/reject`

## Shop order lifecycle

A user order is created as `pending_payment`. It is not debited from the user's
wallet and the product stock is not reduced until the administrator approves it.
On approval, the backend atomically checks the wallet and stock, creates the
purchase transaction, debits the wallet, reduces stock and moves the order to
`paid`/`processing`.
