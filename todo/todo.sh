#!/usr/bin/env bash
# Todo manager v2 with due dates
# Usage: ./todo.sh <user_id> <action> [args...]
# Delegates to todo.py for all actions.

DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$DIR/todo.py" "$@"
