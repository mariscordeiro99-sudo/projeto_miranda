# Politica LGPD operacional

Este documento descreve como o backend trata dados pessoais no Aplicativo Oficial de Comunicacao Institucional.

Importante: este texto e uma politica operacional tecnica para o projeto. Antes de uso oficial por prefeitura/camara, deve ser revisado pelo responsavel juridico ou encarregado de dados da instituicao.

## Finalidade do sistema

O sistema existe para comunicacao institucional oficial entre a administracao publica e cidadaos cadastrados.

Finalidades principais:

- cadastrar cidadaos no aplicativo;
- autenticar usuarios e gestores;
- enviar comunicados oficiais;
- entregar notificacoes push;
- manter historico de comunicados;
- registrar logs de entrega e visualizacao;
- permitir auditoria administrativa;
- atender solicitacoes LGPD de exportacao, exclusao ou desativacao.

## Dados coletados

### Cidadao

Dados principais:

- nome ou primeiro nome;
- username;
- e-mail;
- telefone;
- senha criptografada pelo Django;
- foto de perfil, se enviada;
- tokens de dispositivo para push notification;
- segmentos/grupos de envio, quando usados;
- historico tecnico de entregas e visualizacoes.

### Gestor/administrador

Dados principais:

- username;
- e-mail;
- nome;
- telefone;
- senha criptografada;
- perfil administrativo;
- status ativo/inativo;
- acoes administrativas registradas em auditoria.

### Conteudo institucional

Dados relacionados a comunicados:

- titulo;
- conteudo;
- anexos PDF, Word, imagens e videos;
- autor administrativo;
- data de publicacao;
- status do comunicado.

## Base e justificativa operacional

O tratamento dos dados e necessario para:

- identificar o usuario no sistema;
- permitir login seguro;
- entregar comunicados oficiais;
- evitar envio duplicado de notificacoes;
- medir entrega e visualizacao de comunicados;
- manter seguranca e rastreabilidade administrativa;
- cumprir pedidos de direitos do titular.

## Dados sensiveis

O MVP nao deve solicitar dados sensiveis, como:

- saude;
- religiao;
- opiniao politica;
- biometria;
- origem racial/etnica;
- dados de criancas sem processo apropriado.

Caso algum anexo institucional contenha dado sensivel, a responsabilidade de publicacao deve ser avaliada pelo gestor antes do envio.

## Retencao de dados

Recomendacao operacional:

- usuarios ativos: manter enquanto a conta estiver ativa;
- usuarios desativados: manter dados minimos pelo periodo definido pela instituicao;
- logs de entrega/visualizacao: manter pelo tempo necessario para transparencia e auditoria;
- logs de auditoria: manter por periodo maior, pois registram seguranca e responsabilidade administrativa;
- anexos institucionais: manter enquanto fizerem parte do historico oficial;
- solicitacoes LGPD: manter registro da solicitacao e da conclusao para prova de atendimento.

Uma politica final de prazos deve ser definida pela instituicao responsavel.

## Direitos do cidadao

O backend oferece base tecnica para:

- solicitar exportacao de dados;
- solicitar exclusao de dados;
- solicitar desativacao de conta;
- desativar a propria conta autenticada.

Endpoints:

```http
GET /api/privacy-requests/
POST /api/privacy-requests/
POST /api/privacy/deactivate-account/
```

Tipos de solicitacao:

```text
export
erasure
deactivation
```

Administradores analisam e concluem/rejeitam solicitacoes:

```http
POST /api/privacy-requests/{id}/complete/
POST /api/privacy-requests/{id}/reject/
```

Ao concluir uma solicitacao pendente, o backend executa a acao tecnica conforme
o tipo do pedido:

- `export`: conclui a solicitacao e retorna no corpo da resposta um pacote
  JSON com dados cadastrais, perfil, segmentos, dispositivos, logs de entrega,
  solicitacoes LGPD, auditoria relacionada e comunicados de autoria do usuario.
  Chaves de autenticacao nao sao exportadas; apenas a contagem de tokens ativos.
- `erasure`: anonimiza o usuario, limpa dados de contato, remove tokens de
  autenticacao, desativa/desvincula dispositivos push, remove segmentos,
  anonimiza solicitacoes LGPD relacionadas e desvincula logs de entrega do
  titular. Logs institucionais permanecem sem dados pessoais diretos.
- `deactivation`: desativa a conta, remove tokens de autenticacao e desativa
  dispositivos push, preservando os dados cadastrais para retencao operacional.

Solicitacoes ja resolvidas nao podem ser concluidas novamente. Contas
administrativas exigem tratamento LGPD manual para evitar perda de acesso de
gestao.

## Exclusao e anonimizacao

Ao receber pedido de exclusao, a equipe ainda deve avaliar previamente:

1. se existe obrigacao legal/institucional de manter algum registro;
2. quais dados podem ser apagados;
3. quais dados devem ser anonimizados;
4. quais logs devem permanecer por auditoria.

Ao confirmar a conclusao da solicitacao, o backend aplica:

- desativacao da conta do usuario;
- remocao de tokens de autenticacao ativos;
- remocao de telefone e foto de perfil;
- anonimizacao de nome, email e senha;
- desativacao e desvinculo dos dispositivos push;
- desvinculo de logs de entrega do usuario;
- registrar conclusao no `PrivacyRequest`.

## Desativacao de conta

Cidadaos autenticados podem desativar a propria conta:

```http
POST /api/privacy/deactivate-account/
```

Efeito tecnico:

- `is_active=false`;
- tokens de autenticacao removidos;
- registro de auditoria criado.

Contas administrativas nao podem ser desativadas por esse endpoint. Devem ser gerenciadas pela API de gestores:

```http
POST /api/managers/{id}/deactivate/
POST /api/managers/{id}/revoke/
```

## Auditoria

O backend registra logs administrativos em:

```http
GET /api/audit-logs/
```

Apenas administradores podem acessar.

Acoes auditadas:

- criacao/edicao/publicacao/envio de comunicados;
- criacao/edicao de identidade visual;
- criacao/edicao/desativacao/reativacao/revogacao de gestores;
- criacao/conclusao/rejeicao de solicitacoes LGPD;
- desativacao da propria conta pelo cidadao.

## Acesso interno aos dados

Regras operacionais:

- acesso administrativo deve ser concedido somente a gestores autorizados;
- contas de gestor devem ser individuais;
- nao compartilhar senha administrativa;
- revogar acesso de gestores que sairem da equipe;
- revisar `/api/managers/` periodicamente;
- revisar `/api/audit-logs/` em incidentes ou duvidas.

## Seguranca tecnica

Controles existentes no backend:

- autenticacao por token;
- controle de acesso admin/staff;
- validacao de senha pelo Django;
- throttling em login, cadastro e reset de senha;
- HTTPS/SSL em producao;
- banco com SSL;
- Cloudinary para midia;
- auditoria administrativa;
- validacao de tipo/tamanho/duracao de anexos.

## Incidentes

Em caso de suspeita de vazamento, acesso indevido ou publicacao incorreta:

1. pausar novas publicacoes se necessario;
2. preservar logs de auditoria;
3. identificar usuarios/gestores envolvidos;
4. revogar tokens ou acessos comprometidos;
5. registrar o incidente;
6. acionar responsavel juridico/encarregado de dados;
7. avaliar necessidade de comunicacao aos titulares e autoridades competentes.

## Responsabilidades

Equipe tecnica:

- manter controles de seguranca;
- aplicar migrations;
- manter backup/restore documentado;
- apoiar exportacao/exclusao quando solicitado.

Gestor institucional:

- definir finalidade dos comunicados;
- aprovar conteudos oficiais;
- decidir prazos de retencao;
- responder solicitacoes LGPD;
- manter administradores autorizados.

## Documentos relacionados

```text
backend/docs/PRODUCTION_DEPLOYMENT.md
backend/docs/BACKUP_RESTORE.md
backend/README.md
```
