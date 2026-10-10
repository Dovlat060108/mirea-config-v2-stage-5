#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
expect_failure() {
  if sh run.sh "$@"; then
    echo "Ожидалась ошибка" >&2
    exit 1
  fi
}
expect_failure --script examples/errors.txt --no-repl
expect_failure --script examples/missing.txt --no-repl
expect_failure --unknown
