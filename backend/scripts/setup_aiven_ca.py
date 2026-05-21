#!/usr/bin/env python
"""
Script para baixar o certificado CA da Aiven e configurar a conexão Django.
Execute com: python setup_aiven_ca.py
"""

import os
import sys
import ssl
import requests
from pathlib import Path

def download_aiven_ca():
    """Baixa o certificado CA da Aiven"""
    
    print("=" * 60)
    print("CONFIGURAR CERTIFICADO CA DA AIVEN")
    print("=" * 60)
    
    # Caminhos
    backend_dir = Path(__file__).parent
    ca_dir = backend_dir / 'certs'
    ca_file = ca_dir / 'ca.pem'
    
    # Criar diretório de certificados
    ca_dir.mkdir(exist_ok=True)
    
    # URL do certificado CA da Aiven (certificado Let's Encrypt que eles usam)
    ca_urls = [
        'https://letsencrypt.org/certs/isrgrootx1.pem',  # ISRG Root X1 (RSA)
        'https://letsencrypt.org/certs/isrg-root-x2.pem',  # ISRG Root X2 (ECDSA)
    ]
    
    print(f"\n📥 Tentando baixar certificado CA...\n")
    
    for url in ca_urls:
        try:
            print(f"   Baixando: {url}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(ca_file, 'w') as f:
                    f.write(response.text)
                print(f"   ✅ Certificado baixado e salvo em: {ca_file}")
                return str(ca_file)
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            continue
    
    print("\n⚠️  Não foi possível baixar o certificado.")
    print("   Tentando usar certificados do sistema operacional...")
    
    # Tentar usar certificados do sistema
    system_ca_paths = [
        '/etc/ssl/certs/ca-certificates.crt',  # Linux
        '/etc/ssl/certs/ca-bundle.crt',  # Linux
        '/opt/render/project/src/certs/ca-bundle.crt',  # Render
        '/etc/pki/tls/certs/ca-bundle.crt',  # RedHat
    ]
    
    for ca_path in system_ca_paths:
        if os.path.exists(ca_path):
            print(f"   ✅ Encontrado: {ca_path}")
            return ca_path
    
    print("\n   Nenhum certificado do sistema encontrado.")
    return None

def update_settings():
    """Atualiza o settings.py com o caminho do certificado CA"""
    
    settings_file = Path(__file__).parent / 'core' / 'settings.py'
    
    ca_path = download_aiven_ca()
    if ca_path:
        print(f"\n📝 Atualizando settings.py...")
        print(f"   CA Path: {ca_path}")
        print(f"\n✅ Configure seu env.production com:")
        print(f"   DB_CA_CERT={ca_path}")
    else:
        print("\n⚠️  Não será possível usar SSL sem o certificado CA.")
        print("   Verifique a documentação da Aiven.")

if __name__ == '__main__':
    try:
        update_settings()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
