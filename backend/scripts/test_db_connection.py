#!/usr/bin/env python
"""
Script para testar a conexão com o banco de dados MySQL na Aiven.
Execute com: python test_db_connection.py
"""

import os
import sys
import django
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv('.env.production')

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connections
from django.db.utils import OperationalError

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    
    print("=" * 60)
    print("TESTE DE CONEXÃO COM BANCO DE DADOS AIVEN")
    print("=" * 60)
    
    # Exibe variáveis de conexão (sem expor a senha)
    print(f"\n📋 Variáveis de Conexão Detectadas:")
    print(f"   DB_HOST: {os.getenv('DB_HOST')}")
    print(f"   DB_USER: {os.getenv('DB_USER')}")
    print(f"   DB_NAME: {os.getenv('DB_NAME')}")
    print(f"   DB_PORT: {os.getenv('DB_PORT')}")
    print(f"   DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD', ''))}")
    
    # Tenta conectar
    try:
        connection = connections['default']
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        
        print(f"\n✅ Conexão com sucesso!")
        print(f"   Engine: {connection.settings_dict['ENGINE']}")
        print(f"   Options: {connection.settings_dict.get('OPTIONS', {})}")
        
        # Testa uma query simples
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"   MySQL Version: {version[0]}")
        cursor.close()
        
        return True
        
    except OperationalError as e:
        print(f"\n❌ Erro de Conexão Operacional:")
        print(f"   {str(e)}")
        print(f"\n   Este erro geralmente significa:")
        if "1045" in str(e):
            print(f"   - Credenciais incorretas (usuário/senha)")
            print(f"   - SSL não está sendo negociado corretamente")
            print(f"   - Método de autenticação SHA256_password sem suporte SSL")
        elif "2003" in str(e):
            print(f"   - Host não é acessível")
            print(f"   - IP do Render não está na allowlist da Aiven")
        return False
        
    except Exception as e:
        print(f"\n❌ Erro Inesperado:")
        print(f"   {type(e).__name__}: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_database_connection()
    sys.exit(0 if success else 1)
