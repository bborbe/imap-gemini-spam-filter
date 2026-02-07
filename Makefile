SHELL := /bin/bash

.PHONY: all
all: precommit

.PHONY: install
# Install dependencies (alias for sync)
install: sync

.PHONY: sync
# Sync dependencies
sync:
	@uv sync --all-extras

.PHONY: run
run: spam-filter

.PHONY: spam-filter
spam-filter:
	uv run python -m imap_spam_filter \
		--imap-server="mail.benjamin-borbe.de" \
		--imap-port="993" \
		--imap-username="$$(teamvault-username --teamvault-config ~/.teamvault.json --teamvault-key=xwXyOn)" \
		--imap-password="$$(teamvault-password --teamvault-config ~/.teamvault.json --teamvault-key=xwXyOn)" \
		--gemini-api-key="$$(teamvault-password --teamvault-config ~/.teamvault.json --teamvault-key=eL9BXq)"

.PHONY: list-folders
list-folders:
	uv run python src/imap_spam_filter/list_folders.py \
		--imap-server="mail.benjamin-borbe.de" \
		--imap-port="993" \
		--imap-username="$$(teamvault-username --teamvault-config ~/.teamvault.json --teamvault-key=xwXyOn)" \
		--imap-password="$$(teamvault-password --teamvault-config ~/.teamvault.json --teamvault-key=xwXyOn)"

.PHONY: clean
# Clean build artifacts
clean:
	rm -rf .venv dist *.egg-info .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +

.PHONY: precommit
# Run all precommit checks
precommit: sync format test check
	@echo "All precommit checks passed"

.PHONY: format
# Format code with ruff
format:
	uv run ruff format .
	uv run ruff check --fix . || true

.PHONY: lint
# Lint code with ruff
lint:
	uv run ruff check .

.PHONY: typecheck
# Type check with mypy
typecheck:
	uv run mypy src

.PHONY: check
# Run lint and typecheck
check: lint typecheck

.PHONY: test
# Run tests with pytest
test: sync
	uv run pytest
