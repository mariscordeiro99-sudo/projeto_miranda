#!/usr/bin/env bash
set -e

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
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=== Running migrations ==="
python manage.py migrate

echo ""
echo "=== Build completed successfully ==="
