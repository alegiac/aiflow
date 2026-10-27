#!/bin/sh
set -eu
command -v python3 >/dev/null || { echo "Python 3 richiesto" >&2; exit 1; }
exec python3 "$(dirname "$0")/tools/install_manager.py" install "$@"
