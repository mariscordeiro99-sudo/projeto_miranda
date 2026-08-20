#!/usr/bin/env python
"""
Valida se as variaveis de ambiente do backend estao sendo carregadas.
Nao imprime valores sensiveis.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


backend_dir = Path(__file__).resolve().parent.parent
env_file = None

for filename in ['.env.production', 'env.production', '.env']:
    candidate = backend_dir / filename
    if candidate.exists():
        env_file = candidate
        break

print("=" * 70)
print("VALIDACAO DE VARIAVEIS DE AMBIENTE")
print("=" * 70)
print(f"Script: {Path(__file__).resolve()}")
print(f"Backend: {backend_dir}")
print(f"Arquivo encontrado: {env_file}")
print(f"Existe? {env_file.exists() if env_file else False}")

keys = []
if env_file and env_file.exists():
    load_dotenv(env_file)
    for line in env_file.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            keys.append(line.split('=', 1)[0].strip())

print("\nChaves encontradas:")
for key in keys:
    print(f"   - {key}")

required_vars = ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']

print("\nVariaveis obrigatorias:")
for var in required_vars:
    value = os.getenv(var)
    status = "OK" if value else "MISSING"
    print(f"   {var}: {status}")

print("=" * 70)
