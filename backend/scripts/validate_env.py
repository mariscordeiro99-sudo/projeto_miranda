#!/usr/bin/env python
"""
Script para validar se as variáveis de ambiente estão sendo carregadas corretamente.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Localiza o arquivo .env.production
backend_dir = Path(__file__).parent
env_file = None

# Tenta diferentes nomes
for filename in ['.env.production', 'env.production', '.env']:
    candidate = backend_dir / filename
    if candidate.exists():
        env_file = candidate
        break

print("=" * 70)
print("VALIDAÇÃO DE VARIÁVEIS DE AMBIENTE")
print("=" * 70)

print(f"\n📁 Caminho do Script: {Path(__file__).resolve()}")
print(f"📁 Diretório Backend: {backend_dir}")
print(f"📁 Arquivo encontrado: {env_file}")
print(f"   Existe? {env_file.exists() if env_file else False}")

if env_file and env_file.exists():
    print(f"\n📄 Conteúdo do arquivo (sem valores sensíveis):")
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line:
                key = line.split('=')[0]
                print(f"   ✅ {key}")

    # Carrega o arquivo
    print(f"\n⏳ Carregando arquivo...")
    load_dotenv(env_file)

# Verifica as variáveis
print(f"\n✅ Variáveis carregadas no os.environ:")
required_vars = ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']

for var in required_vars:
    value = os.getenv(var)
    status = "✅" if value else "❌"
    masked = value[:10] + "***" if value and len(value) > 10 else value
    print(f"   {status} {var}: {masked}")

print("\n" + "=" * 70)

# Se tudo OK, tenta PyMySQL
if all(os.getenv(var) for var in required_vars):
    print("\n🔐 Tentando conexão com PyMySQL...")
    try:
        import pymysql
        
        conn = pymysql.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            charset='utf8mb4',
            connect_timeout=5
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        
        print(f"   ✅ SUCESSO! Conectado ao MySQL")
        print(f"   Version: {version[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Erro: {type(e).__name__}: {e}")
else:
    print("\n❌ Variáveis faltando! Não é possível conectar.")
