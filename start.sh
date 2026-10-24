#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  for candidate in "${VENV_PATH:-}" "$SCRIPT_DIR/venv" "$SCRIPT_DIR/.venv" "$SCRIPT_DIR/../env"; do
    if [[ -n "$candidate" && -f "$candidate/bin/activate" ]]; then
      # shellcheck disable=SC1091
      source "$candidate/bin/activate"
      break
    fi
  done
fi

if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  echo "Advertencia: no se detectó un entorno virtual; se usará el Python del sistema." >&2
fi

export PYTHONPATH="$SCRIPT_DIR${PYTHONPATH:+:$PYTHONPATH}"
export FLASK_APP=run.py

echo "Iniciando Sistema de Detección de TB..."
exec python3 run.py
