.DEFAULT_GOAL := help

.PHONY: help up up-d down build logs migrate makemigrations seed superuser \
        close-auctions backend-shell frontend-shell backend-test frontend-test test clean clear-cache

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/' | sort

up: ## Build and start db, backend, frontend (foreground, logs streaming)
	docker compose up --build

up-d: ## Same as `up` but detached
	docker compose up --build -d

down: ## Stop and remove containers
	docker compose down

build: ## Rebuild images without starting
	docker compose build

logs: ## Tail logs for all services
	docker compose logs -f

migrate: ## Apply Django migrations
	docker compose exec backend python manage.py migrate

makemigrations: ## Generate new Django migrations
	docker compose exec backend python manage.py makemigrations

seed: ## Load the One Piece TCG card catalog + demo users/auctions
	docker compose exec backend python manage.py seed_cards
	docker compose exec backend python manage.py seed_demo

close-auctions: ## Close auctions whose end_time has passed (SOLD/EXPIRED)
	docker compose exec backend python manage.py close_expired_auctions

superuser: ## Create a Django admin superuser
	docker compose exec backend python manage.py createsuperuser

backend-shell: ## Open a shell in the backend container
	docker compose exec backend sh

frontend-shell: ## Open a shell in the frontend container
	docker compose exec frontend sh

backend-test: ## Run backend test suite (pytest)
	docker compose exec backend pytest

frontend-test: ## Run frontend test suite (jest)
	docker compose exec frontend npm test

test: backend-test frontend-test ## Run both test suites

clear-cache: ## Clear the Next.js build cache (fixes stale chunk errors, keeps db data)
	docker compose down
	docker volume rm $$(docker volume ls -q --filter name=frontend_next) 2>/dev/null || true
	docker compose up -d

clean: ## Stop containers and remove volumes (DESTROYS db data + media)
	docker compose down -v
