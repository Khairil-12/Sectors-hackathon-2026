#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "==> [1/4] Installing frontend dependencies..."
npm ci --prefer-offline --no-audit || npm install --no-audit

echo "==> [2/4] Compiling Tailwind CSS bundle..."
npm run build

echo "==> [3/4] Installing Python dependencies..."
if command -v uv &> /dev/null; then
    uv sync --frozen || uv sync
    PYTHON_CMD="uv run python"
else
    pip install -r pyproject.toml || pip install -e .
    PYTHON_CMD="python"
fi

echo "==> [4/4] Running database migrations and collectstatic..."
$PYTHON_CMD manage.py migrate --noinput
$PYTHON_CMD manage.py collectstatic --noinput --clear

echo "==> Build completed successfully!"
