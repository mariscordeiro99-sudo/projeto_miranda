#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

# Exportar variáveis obrigatoriamente para os processos filhos
export DB_NAME="${DB_NAME:-defaultdb}"
export DB_USER="${DB_USER:-avnadmin}"
export DB_PASSWORD="${DB_PASSWORD}"
export DB_HOST="${DB_HOST}"
export DB_PORT="${DB_PORT:-3306}"
export PYTHONUNBUFFERED=1

echo "=== Django Build Script ==="
echo "Database Host: $DB_HOST"
echo "Database Port: $DB_PORT"
echo ""

echo "=== Installing dependencies ==="
python -m pip install --disable-pip-version-check --no-input -r requirements.txt

echo ""
echo "=== Running migrations ==="
python manage.py migrate

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] || [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo ""
    echo "=== Creating/updating Django admin user ==="
    python manage.py upsert_admin
fi

echo ""
echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo ""
echo "=== Build completed successfully ==="
