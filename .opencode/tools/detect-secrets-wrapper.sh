#!/usr/bin/env bash
# Wrapper for detect-secrets pre-commit hook.
# Skips scanning unless .secrets.baseline exists in the project root.
# When present, enforces the baseline against staged files.
test -f .secrets.baseline || exit 0
detect-secrets-hook --baseline .secrets.baseline "$@"