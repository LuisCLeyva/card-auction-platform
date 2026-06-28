# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands assume the stack is running (`make up` / `make up-d`). See `make help` for the full list.

### Stack lifecycle
- `make up` / `make up-d` — build and start `db` + `backend` + `frontend` (foreground / detached)
- `make down` — stop and remove containers but **keep** volumes (db data + media survive)
- `make clear-cache` — clears the Next.js build cache volume (fixes stale chunk errors like `Cannot find module './418.js'`), keeps db data
- `make clean` — `docker compose down -v`: stops containers **and destroys all volumes** (db data + media gone)
- `make migrate` — apply Django migrations
- `make makemigrations` — generate migrations after model changes (commit the generated files — they don't get created by tests)
- `make seed` — `seed_cards` (loads the card catalog) then `seed_demo` (demo users/inventory/auctions)
- `make close-auctions` — run `close_expired_auctions` (settles anything past `end_time`)
- `make superuser` — create a Django admin user
- `make backend-shell` / `make frontend-shell` — shell into a container

### Backend tests (pytest-django)
- All: `docker compose exec backend pytest` (or `make backend-test`)
- Single file: `docker compose exec backend pytest auctions/tests.py`
- Single test: `docker compose exec backend pytest auctions/tests.py::test_bid_raises_the_current_price`
- Outside Docker: from `backend/`, activate `venv` and run `pytest` directly; point at the Dockerized Postgres with `POSTGRES_HOST=localhost python manage.py <cmd>` (e.g. for `makemigrations`/`migrate`/`seed_cards` without starting the backend container).

`conftest.py` provides shared fixtures: `api_client` (DRF `APIClient` with `enforce_csrf_checks=True` — tests exercise the real CSRF flow), `make_user`, `user`, `other_user`, `make_card`, `card`, `make_card_copy`, `card_copy`, `make_auction`, `auction`, and `login_as` (calls `GET /api/auth/csrf/` + `POST /api/auth/login/` and returns the csrftoken). All `make_*` fixtures are factory functions that accept keyword overrides.

### Frontend tests (Jest + Testing Library)
- All: `docker compose exec frontend npm test` (or `make frontend-test`)
- Watch mode: `docker compose exec frontend npm run test:watch`
- Single file: `docker compose exec frontend npx jest components/CountdownTimer.test.tsx`

### Frontend lint/build
- `docker compose exec frontend npm run lint`
- `docker compose exec frontend npm run build`

## Architecture

### Data model layering
`cards.Card` (read-only catalog, seeded from `backend/cards/fixtures/op01.csv` + matching images, never edited through the API) → `inventory.CardCopy` (a user's owned copy: condition/quantity — this is the "My Cards" feature) → `auctions.Auction` (lists exactly one `CardCopy`) → `auctions.Bid`. An `Auction` never references the catalog directly, always through a `CardCopy` — ownership ("can I list this?") and listing state (`CardCopy.is_listed`) are enforced at the inventory layer, not duplicated onto the auction.

### Auth: JWT-in-httpOnly-cookie + CSRF
SimpleJWT issues the tokens, but they're set as httpOnly cookies (`accounts/views.py`), never returned in response bodies. `accounts/authentication.py`'s `CookieJWTAuthentication` reads `access_token` from cookies instead of an `Authorization` header, and — for unsafe HTTP methods — runs the *same* `CSRFCheck` DRF's `SessionAuthentication` uses internally, checking the `csrftoken` cookie against an `X-CSRFToken` header (httpOnly stops XSS token theft, not CSRF, since the cookie still rides along on cross-site requests).

`register`/`login`/`refresh`/`logout` set `authentication_classes = []` deliberately. `refresh` in particular must work *because* the access token is expired/invalid, so it can't depend on that same token authenticating first. This also sidesteps a DRF quirk where `AuthenticationFailed` silently becomes a 403 instead of 401 when a view has no authenticator configured — `LoginView` catches it explicitly to restore the 401 (see the comment there).

### Auction lifecycle and concurrency
Business rules live in `auctions/serializers.py` (`AuctionSerializer.validate()`) and `auctions/views.py` (`AuctionViewSet`): edit/cancel are seller-only and blocked once any bid exists, so terms can't change underneath a bidder. `bid` and `buy-now` run inside `transaction.atomic()` with `select_for_update()` on the `Auction` row to avoid a lost-update race between two concurrent bids. `close_expired_auctions` is a plain management command (no Celery/worker in this stack by design) — run it manually or on a schedule to settle auctions past `end_time` into `SOLD`/`EXPIRED`.

### Two frontend fetch helpers, on purpose
- `lib/api.ts` (`apiFetch`) — for Client Components. Browser-driven: cookies attach automatically, an `X-CSRFToken` header is injected for unsafe methods, and a 401 triggers one silent refresh-and-retry.
- `lib/server-api.ts` (`serverFetch`) — for Server Components. Server-to-server: httpOnly cookies are **not** forwarded automatically, so they're read via `next/headers` and attached manually; the backend is reached via `INTERNAL_API_URL` (`http://backend:8000`, the Docker service name), not `NEXT_PUBLIC_API_URL` (`http://localhost:8000`, what the browser uses).

### Card image URLs must resolve from inside the frontend container
`cards/serializers.py` builds absolute image URLs from `settings.MEDIA_BASE_URL`, which is the Docker-internal backend address (`http://backend:8000`), **not** the browser-facing host — this is intentional, not a leftover bug. `next/image` always re-fetches the image server-side via `/_next/image?url=...` regardless of whether the surrounding page was server- or client-rendered, so the URL has to resolve from wherever that Next.js server process runs (the frontend container), or the optimizer 500s.

### Edge auth check
`middleware.ts` gates `/dashboard/*`, `/auctions/create`, and `/auctions/:id/edit` by verifying the `access_token` cookie's JWT signature at the edge with `jose`, using `JWT_SIGNING_KEY` shared with the backend via the root `.env`. Reading and verifying the cookie server-side is fine — httpOnly only blocks *client-side JS* from reading it.

### Seed data
`backend/cards/fixtures/` contains a real One Piece TCG set (-ROMANCE DAWN- [OP01], 121 cards with art), committed to the repo so the project is self-contained. `seed_cards` dedupes the source CSV by `card_id` (it repeats a row per alt-art image variant) and splits the catalog's `LifeN`/numeric `cost` string into separate `life`/`cost` model fields.

### Single shared `.env`
One root `.env` (see `.env.example`) feeds all three docker-compose services via `env_file`. There's no per-service secret isolation — the frontend container, for instance, also receives `POSTGRES_PASSWORD` even though it never uses it.

### API conventions
- Routes: `/api/auth/`, `/api/cards/`, `/api/inventory/`, `/api/auctions/`.
- Any CSRF-required request (unsafe method with `CookieJWTAuthentication`) needs a prior `GET /api/auth/csrf/` to receive the `csrftoken` cookie; the token is then echoed back as `X-CSRFToken`. This is why `login_as` in `conftest.py` does a `GET /api/auth/csrf/` before the login `POST`.
- Auction list supports `?status=ACTIVE|SOLD|CANCELLED|EXPIRED` and `?mine=1` (returns only the authenticated user's auctions).
- Paginated responses (`Paginated<T>`) have shape `{count, next, previous, results[]}`. Default page size is 20; `?page_size=N` up to 200.
- `CardCopy.is_listed` is a computed property (checks for an ACTIVE auction), not a database column — no migration needed when its logic changes.
