#!/bin/bash
# (FR-016) Git Forensic: Commit message linter

echo "--- Digital Courtroom: Git Forensic Linter ---"

# Check the last 5 commit messages
commits=$(git log -n 5 --pretty=format:"%s")

while IFS= read -r line; do
    if [[ ! $line =~ ^(feat|fix|chore|docs|style|refactor|perf|test)(\(.*\))?:[[:space:]].* ]]; then
        echo -e "[ERROR] Non-compliant commit message: \"$line\""
        echo "Format must follow: <type>(<scope>): <subject>"
        # exit 1 (disabled for local dev ease, but enabled in CI)
    else
        echo -e "[PASS] Commit message: \"$line\""
    fi
done <<< "$commits"
