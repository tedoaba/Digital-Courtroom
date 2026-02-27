# Variables
REPO ?=
SPEC ?=
RUBRIC ?= rubric/week2_rubric.json

# Portability Logic
ifeq ($(OS),Windows_NT)
    # Check if we're in a POSIX-like shell (Git Bash, MSYS2)
    ifneq (,$(findstring /sh,$(SHELL)))
        MKDIR_P := mkdir -p
        NULL := /dev/null
        RM := rm -f
        RMDIR := rm -rf
    else
        MKDIR_P := mkdir
        NULL := nul
        RM := del /Q
        RMDIR := rmdir /S /Q
    endif
else
    MKDIR_P := mkdir -p
    NULL := /dev/null
    RM := rm -f
    RMDIR := rm -rf
endif

# Internal Checks
.check-uv:
	@uv --version > $(NULL) 2>&1 || (echo "ERROR: uv MISSING detected. Run 'make setup' or create FILE."; exit 1)

.check-env:
	@if [ -f .env ] || [ -f .env.example ]; then true; else echo "ERROR: .env MISSING detected. Run 'make setup' or create FILE."; exit 1; fi

.check-dirs:
	@if [ ! -d audit ]; then $(MKDIR_P) audit; fi
	@if [ ! -d reports ]; then $(MKDIR_P) reports; fi

help:
	@echo "Digital Courtroom - Available Targets:"
	@echo "  make run REPO=... SPEC=...   - Execute a standard audit"
	@echo "  make cli                     - Launch the courtroom TUI"
	@echo "  make test                    - Run all unit and integration tests"
	@echo "  make lint                    - Run ruff for python linting"
	@echo "  make docker-build             - Build the Digital Courtroom image"
	@echo "  make docker-run SPEC=...      - Run the containerized auditor"
	@echo "  make clean                   - Remove build and test artifacts"

run: .check-uv .check-env .check-dirs
	uv run audit --repo "$(REPO)" --spec "$(SPEC)" --rubric "$(RUBRIC)"

cli: .check-uv .check-env
	uv run courtroom

test: .check-uv
	uv run pytest tests/ --cov=src --cov-report=term-missing

lint: .check-uv
	uv run ruff check .
	uv run ruff format --check .

docker-build:
	docker build -t digital-courtroom:latest .

docker-run: .check-env
	docker run --rm -it \
		--env-file .env \
		-v "$(shell pwd)/reports:/reports:ro" \
		-v "$(shell pwd)/audit:/audit:rw" \
		digital-courtroom:latest \
		audit --repo "$(REPO)" --spec "/reports/$(notdir $(SPEC))" --rubric "$(RUBRIC)"

clean:
	$(RMDIR) .pytest_cache .ruff_cache .venv audit reports || true
	$(RM) *.log || true
