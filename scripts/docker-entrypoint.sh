#!/bin/bash
set -e

echo "--- Digital Courtroom Entrypoint ---"

# Verify volume mappings
if [ ! -d "/reports" ]; then
    echo "ERROR: Required volume mapping /reports is missing. Use -v argument or make docker-run."
    exit 1
fi

if [ ! -d "/audit" ]; then
    echo "ERROR: Required volume mapping /audit is missing. Use -v argument or make docker-run."
    exit 1
fi

# Verify critical environment variables
if [ -z "$GOOGLE_API_KEY" ] && [ -z "$LANGCHAIN_API_KEY" ]; then
    echo "WARNING: No API keys (GOOGLE_API_KEY or LANGCHAIN_API_KEY) detected. System might fail during audit."
fi

# Execute command
exec "$@"
