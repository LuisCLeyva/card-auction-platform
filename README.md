# Card Auction House

A full-stack trading-card auction platform: list cards from your personal
collection, run timed auctions with bidding and an optional Buy Now price,
and manage everything through a dark/gold "card game" themed UI.

- **Backend**: Django + Django REST Framework, JWT auth (SimpleJWT) carried
  in httpOnly cookies, PostgreSQL.
- **Frontend**: Next.js (App Router, TypeScript, Tailwind CSS).
- **Catalog data**: seeded from a real One Piece TCG set (-ROMANCE DAWN-
  [OP01], 121 cards with art), included in the repo under
  `backend/cards/fixtures/`.

## Architecture

```
card-auction-platform/
├── backend/                 Django project
│   ├── config/               settings, urls, DRF/JWT/pagination config
│   ├── accounts/              custom email-based User, JWT-cookie auth, CSRF endpoint
│   ├── cards/                 read-only card catalog + seed_cards command
│   ├── inventory/              a user's owned card copies ("My Cards")
│   ├── auctions/               Auction + Bid models, bid/buy-now/cancel actions
│   └── conftest.py / pytest.ini   pytest-django fixtures and config
├── frontend/                 Next.js app
│   ├── app/                    routes (App Router)
│   ├── components/             AuctionCard, CountdownTimer, Navbar, Field
│   ├── lib/                    api.ts (client fetch), server-api.ts (SSR fetch), types
│   └── middleware.ts            edge JWT check for protected routes
├── docker-compose.yml
├── .env.example
└── Makefile
```

### Data model

- `cards.Card` — read-only catalog (the actual trading card data: name,
  rarity, cost, power, effect text, art). Seeded once from CSV; nobody
  edits it through the API.
- `inventory.CardCopy` — a specific copy a user owns (condition, quantity).
  This is "My Cards" — add/edit/remove your own copies.
- `auctions.Auction` — lists one `CardCopy` for sale: starting price,
  optional buy-now price, status, start/end time, winner.
- `auctions.Bid` — one bid on an auction (`is_buy_now` flags a Buy Now).

An auction always points at an inventory copy rather than the catalog
directly, so "who owns this card" and "what's it listed for" are separate
concerns — you can't auction a card you don't own, and a copy can only be
in one active auction at a time (`CardCopy.is_listed`).

### Auth: JWT in httpOnly cookies + CSRF

Access/refresh tokens are issued by SimpleJWT but never touch JS — they're
set as `httpOnly` cookies (`accounts/views.py`). A custom DRF authentication
class (`accounts/authentication.py`) reads the access token cookie instead
of an `Authorization` header.

httpOnly only stops *client-side JS* from reading the token (mitigating
token theft via XSS) — it does **not** stop CSRF, since the browser still
attaches the cookie automatically on cross-site requests. So every
state-changing request also needs an `X-CSRFToken` header, whose value
comes from a separate, readable `csrftoken` cookie (Django's standard CSRF
cookie, fetched once via `GET /api/auth/csrf/`). The backend reuses DRF's
own `CSRFCheck` (the same mechanism `SessionAuthentication` uses) so the
verification logic is identical to Django's well-tested default — see
`enforce_csrf()` in `accounts/authentication.py`.

`login` / `register` / `refresh` / `logout` deliberately skip this cookie
authentication class (`authentication_classes = []`): refresh in particular
must work *because* the access token is expired, so it can't depend on that
same token being valid.

### Next.js middleware + the two fetch helpers

`middleware.ts` protects `/dashboard/*`, `/auctions/create`, and
`/auctions/:id/edit`. It reads the `access_token` cookie directly (a
server-side read of an httpOnly cookie is fine — only browser JS is
blocked) and verifies its signature at the edge with `jose`, redirecting to
`/login` if it's missing, invalid, or expired.

There are two fetch helpers because cookies behave differently depending on
where the request originates:

- `lib/api.ts` (`apiFetch`) — for Client Components. Runs in the browser,
  so cookies are attached automatically (`credentials: "include"`); it
  injects `X-CSRFToken` on unsafe methods and silently refreshes + retries
  once on a 401.
- `lib/server-api.ts` (`serverFetch`) — for Server Components. Runs
  server-side, so httpOnly cookies are **not** forwarded automatically on
  this server-to-server call — it reads them via `next/headers` and attaches
  them manually. It also talks to the backend via `INTERNAL_API_URL`
  (`http://backend:8000`, the Docker service name) instead of
  `NEXT_PUBLIC_API_URL` (`http://localhost:8000`, what the browser uses).

### Auction lifecycle

- **Create**: pick an unlisted `CardCopy`, set a starting price, optional
  buy-now price, and an end time.
- **Edit/Cancel**: seller-only, and only while the auction has **no bids**
  — once someone has bid, the terms can't change underneath them. Cancel is
  a status transition (`CANCELLED`), not a delete, so history is kept.
- **Bid**: must clear `current_price + min_increment` (or the starting
  price, for the first bid). Bidding at or above the buy-now price closes
  the auction immediately as `SOLD`.
- **Buy Now**: a dedicated action that closes the auction immediately at
  the buy-now price.
- **Expiry**: `python manage.py close_expired_auctions` (run on a schedule
  in production — cron/Celery beat; `make close-auctions` for local/manual
  use) marks any auction whose `end_time` has passed as `SOLD` (highest
  bidder wins) or `EXPIRED` (no bids).

All money-moving actions (`bid`, `buy-now`) run inside a DB transaction with
`select_for_update()` on the auction row to avoid a race between two
concurrent bids.

## Quickstart

Requires Docker and Docker Compose.

```bash
cp .env.example .env        # already done for you if you cloned this repo as-is — edit secrets for real use
make up                     # builds and starts db, backend, frontend
make migrate                # in another terminal, once the db is healthy
make seed                   # loads the card catalog + demo users/auctions
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Django admin: http://localhost:8000/admin/ (`make superuser` to create an account)

Demo accounts created by `make seed` (password for all: `DemoPass123!`):
`alice@example.com`, `bob@example.com`, `carol@example.com`, `dave@example.com`.

Run `make help` for the full list of commands (tests, shells, closing
expired auctions, etc).

## Environment variables

See `.env.example` for the full list with comments. Highlights:

| Variable | Purpose |
|---|---|
| `POSTGRES_*` | Database name/user/password, shared by `db` and `backend` |
| `DJANGO_SECRET_KEY` | Django's cryptographic secret |
| `JWT_SIGNING_KEY` | Signs/verifies JWTs — shared with the frontend's `middleware.ts` |
| `JWT_COOKIE_SECURE` | Set to `1` once served over HTTPS |
| `NEXT_PUBLIC_API_URL` | Backend URL as seen by the **browser** |
| `INTERNAL_API_URL` | Backend URL as seen by the **frontend container** (Server Components) |

## Testing

```bash
make backend-test     # pytest-django: auth, CSRF, inventory ownership rules,
                       # auction create/edit/cancel rules, bidding + buy-now,
                       # the close_expired_auctions command
make frontend-test     # jest: CountdownTimer (no hydration mismatch, ticks
                       # down, shows "Ended"), the api client (CSRF header,
                       # silent-refresh-on-401, error parsing)
make test              # both
```

## Notable simplifications (called out, not hidden)

- Single shared `.env` for all services — a stricter setup would split
  secrets per service so the frontend container never sees `POSTGRES_PASSWORD`,
  `DJANGO_SECRET_KEY`, etc. (it does need `JWT_SIGNING_KEY` and `INTERNAL_API_URL`).
- `close_expired_auctions` is a manual/cron-style command, not a background
  worker — there's no Celery here by design, to keep the stack to exactly
  the three requested services.
- No e2e browser tests (Playwright) — component/unit tests cover the
  trickiest client logic (the countdown timer's hydration-safe rendering,
  the API client's CSRF + refresh flow); manual testing covered the rest.
