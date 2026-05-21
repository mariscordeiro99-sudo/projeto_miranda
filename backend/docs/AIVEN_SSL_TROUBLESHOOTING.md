# Resolução de Erro 1045 - MySQL Aiven no Render

## Erro Atual
```
(1045, "Acesso negado para o usuário 'avnadmin'@'74.220.48.30' (usando senha: SIM)")
```

## Causas Possíveis

### 1. **SSL não está sendo forçado corretamente**
- Aiven exige SSL obrigatório
- `mysqlclient` pode não estar negociando SSL corretamente

### 2. **Certificado CA faltando ou inválido**
- Aiven usa certificados Let's Encrypt
- Pode ser necessário especificar o CA manualmente

### 3. **Método de autenticação incompatível**
- Aiven usa `caching_sha2_password` que requer SSL
- Sem SSL, a autenticação falha com erro 1045

---

## Solução: Passo a Passo

### Opção A: Usar Variável de Certificado CA (Recomendado)

1. **Verifique se o Render tem certificado CA:**
   ```bash
   ls -la /etc/ssl/certs/ca-certificates.crt
   # ou
   ls -la /opt/render/project/src/certs/
   ```

2. **Se encontrou, adicione no Render Environment:**
   ```
   DB_CA_CERT=/etc/ssl/certs/ca-certificates.crt
   ```

3. **Ou baixe o certificado da Aiven:**
   ```bash
   python backend/setup_aiven_ca.py
   ```

### Opção B: Usar a String de Conexão Completa da Aiven

Você já tem no `env.production`:
```
DB_server=mysql://avnadmin:YOUR_PASSWORD@mysql-15d78340-projeto-miranda.a.aivencloud.com:19616/defaultdb?ssl-mode=REQUIRED
```

Adicione no Render Environment:
```
DATABASE_URL=mysql://avnadmin:YOUR_PASSWORD@mysql-15d78340-projeto-miranda.a.aivencloud.com:19616/defaultdb?ssl-mode=REQUIRED
```

### Opção C: Usar PyMySQL como Driver (Alternativa)

Se `mysqlclient` continua falhando:

1. **Instale PyMySQL:**
   ```bash
   pip install PyMySQL
   ```

2. **Adicione ao `manage.py`:**
   ```python
   import pymysql
   pymysql.install_as_MySQLdb()
   ```

3. **Mude o ENGINE no settings.py:**
   ```python
   'ENGINE': 'django.db.backends.mysql',  # Continua igual, mas usa PyMySQL
   ```

---

## Como Testar Localmente

```bash
# Com as variáveis de ambiente carregadas
python backend/test_db_connection.py
```

Se funcionar localmente, o problema é apenas com o IP do Render na Aiven.

---

## Se Ainda Não Funcionar

### Verifique na Aiven Console:

1. **MySQL Service → Network → IP Allowlist**
   - Certifique-se de que `74.220.48.30/32` está adicionado
   - Ou `74.220.48.0/24` para a range completa

2. **MySQL Service → Users**
   - Clique em `avnadmin`
   - Verifique se está com `caching_sha2_password` ou `native`
   - Se for `native`, mude para `caching_sha2_password` (requer SSL)

3. **Test Connection na Aiven:**
   - Aiven Console → MySQL Service → Overview
   - Clique em "Connect"
   - Teste com o comando mysql-client

---

## Configuração Final no Render

Adicione estas variáveis de ambiente no Render Dashboard:

```
DB_NAME=defaultdb
DB_USER=avnadmin
DB_PASSWORD=YOUR_AIVEN_PASSWORD
DB_HOST=mysql-15d78340-projeto-miranda.a.aivencloud.com
DB_PORT=19616
DB_CA_CERT=/etc/ssl/certs/ca-certificates.crt
ALLOWED_HOSTS=projeto-miranda.onrender.com,localhost
```

---

## Logs Úteis para Debug

No Render Deploy Logs:
```
python -c "import django; django.setup(); from django.db import connections; c=connections['default']; print(c.settings_dict['OPTIONS'])"
```

No Django Shell:
```bash
python manage.py shell
>>> from django.db import connections
>>> db = connections['default']
>>> db.ensure_connection()  # Tenta conectar
>>> db.connection.get_server_info()  # Se funcionar, mostra versão do MySQL
```
