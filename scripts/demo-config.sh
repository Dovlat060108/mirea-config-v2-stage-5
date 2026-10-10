#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
sh run.sh --help
sh run.sh --vfs examples/vfs.json --no-repl
sh run.sh --script examples/startup.txt --no-repl
sh run.sh --vfs examples/vfs.json --script examples/startup.txt --no-repl
