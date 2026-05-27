#!/usr/bin/env python
"""
Script para testar a conexao com o banco de dados configurado no backend.
Execute com: python scripts/test_db_connection.py
"""

import os
import sys

import django
from dotenv import load_dotenv


backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

for filename in ['.env.production', 'env.production', '.env']:
    env_path = os.path.join(backend_dir, filename)
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connections  # noqa: E402
from django.db.utils import OperationalError  # noqa: E402


def test_database_connection():
    print("=" * 60)
    print("TESTE DE CONEXAO COM BANCO DE DADOS")
    print("=" * 60)

    print("\nVariaveis de conexao detectadas:")
    print(f"   DB_HOST: {os.getenv('DB_HOST')}")
    print(f"   DB_USER: {os.getenv('DB_USER')}")
    print(f"   DB_NAME: {os.getenv('DB_NAME')}")
    print(f"   DB_PORT: {os.getenv('DB_PORT')}")
    print(f"   DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD', ''))}")

    try:
        connection = connections['default']
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()

        print("\nConexao com sucesso!")
        print(f"   Engine: {connection.settings_dict['ENGINE']}")
        print(f"   Options: {connection.settings_dict.get('OPTIONS', {})}")

        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"   MySQL Version: {version[0]}")
        cursor.close()

        return True

    except OperationalError as error:
        print("\nErro de conexao operacional:")
        print(f"   {error}")
        print("\n   Este erro geralmente significa:")
        if "1045" in str(error):
            print("   - Credenciais incorretas (usuario/senha)")
            print("   - SSL nao esta sendo negociado corretamente")
            print("   - Metodo de autenticacao SHA256_password sem suporte SSL")
        elif "2003" in str(error):
            print("   - Host nao esta acessivel")
            print("   - IP da maquina nao esta na allowlist do provedor")
        return False

    except Exception as error:
        print("\nErro inesperado:")
        print(f"   {type(error).__name__}: {error}")
        return False


if __name__ == '__main__':
    success = test_database_connection()
    sys.exit(0 if success else 1)
