# Conexão segura com MySQL Aiven

Este guia descreve a configuração da conexão entre o backend e o Aiven sem registrar credenciais no repositório.

## Regras de segurança

- configure senhas somente no gerenciador de variáveis do ambiente de hospedagem;
- nunca inclua usuário, senha ou URL real do banco em arquivos versionados;
- use uma conta de banco exclusiva para cada ambiente;
- rotacione imediatamente qualquer credencial que tenha sido exposta.

## Variáveis de ambiente

Use uma URL completa ou variáveis separadas. Todos os valores abaixo são exemplos.

```env
DATABASE_URL=mysql://USUARIO:SENHA@HOST:PORTA/NOME_DO_BANCO
DB_SSL_REQUIRED=true
DB_CA_CERT=/caminho/para/ca.pem
```

Como alternativa:

```env
DB_NAME=nome_do_banco
DB_USER=usuario_do_banco
DB_PASSWORD=senha_gerenciada_fora_do_git
DB_HOST=host-do-servico.aivencloud.com
DB_PORT=12345
DB_SSL_REQUIRED=true
DB_CA_CERT=/caminho/para/ca.pem
```

`DB_CA_CERT` pode receber o caminho do certificado. Quando o provedor exigir o conteúdo do certificado em vez do caminho, use `DB_CA_CERT_CONTENT` no ambiente seguro.

## Diagnóstico

1. Confirme se o serviço MySQL está ativo.
2. Confira host, porta, usuário e nome do banco no painel do Aiven.
3. Valide a lista de IPs permitidos.
4. Confirme que o certificado CA pertence ao serviço correto.
5. Teste a conexão sem imprimir a URL ou a senha nos logs.

No backend, execute:

```bash
python manage.py check
python manage.py migrate --plan
```

## Erro 1045

O erro de acesso negado normalmente indica credencial inválida, usuário sem permissão, origem não autorizada ou negociação SSL incorreta. Redefina a senha no Aiven se houver qualquer suspeita de exposição e atualize a variável correspondente no ambiente de hospedagem.
