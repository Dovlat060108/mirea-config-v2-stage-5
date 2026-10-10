#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
for file in minimal files vfs; do
  sh run.sh --vfs "examples/$file.json" --script examples/load.txt --no-repl
done
if sh run.sh --vfs examples/missing.json --no-repl; then
  echo "Ожидалась ошибка загрузки" >&2
  exit 1
fi
