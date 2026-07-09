# STATUS — onde paramos (Desapega)

> Atualize ao fim de cada sessão. É o primeiro lugar a ler quando voltar.

## Sessão atual
- **Data:** 2026-07-09
- **Fase atual:** FASES 0, 1, 2, 3, 4 e 5 CONCLUÍDAS ✅ → próxima é a Fase 6
  (favoritos + perfil público).

## Fase 5 — chat comprador↔vendedor (2026-07-09) ✅ testada ponta-a-ponta
- **Models** (`models.py`): `Conversa` (anuncio FK related_name='conversas',
  comprador FK related_name='conversas_iniciadas', criado_em;
  `unique_together=('anuncio','comprador')`, ordering `-criado_em`) e `Mensagem`
  (conversa FK related_name='mensagens', autor FK related_name='mensagens_enviadas',
  texto, criado_em, `lida` BooleanField default False; ordering `criado_em`).
  Migration `0003_conversa_mensagem` aplicada.
- **Views** (`views.py`): `iniciar_conversa(pk)` (pk=anúncio; bloqueia dono
  consigo mesmo; `get_or_create`), `detalhe_conversa(pk)` (pk=conversa; guarda:
  só comprador OU anuncio.vendedor; POST grava msg e faz PRG redirect),
  `minhas_conversas` (inbox: `como_comprador` e `como_vendedor`). Import dos
  models atualizado com `Conversa, Mensagem`.
- **URLs**: `conversas/` (minhas_conversas), `anuncio/<pk>/conversar/`
  (iniciar_conversa), `conversa/<pk>/` (conversa).
- **Templates** (Claude criou): `conversa.html` (thread com bolhas minha/outro +
  form textarea) e `inbox.html` (seções Comprando/Vendendo). Editados:
  `detalhe.html` (botão "💬 Conversar com o vendedor" p/ não-dono logado; convite
  a logar p/ anônimo) e `base.html` (link "Conversas" no menu).
- **CSS**: bloco `.chat-topo/.chat-thread/.msg/.msg-bolha/.chat-form/.inbox-secao/
  .conversa-item` no fim do `style.css`.
- **Teste:** gabri (comprador) ↔ maria_teste (vendedor) trocaram mensagens no
  anúncio "Bicicleta Caloi aro 29". OK.
- **Dado de teste novo:** senha do `maria_teste` foi definida como `teste12345`
  (via shell) pra permitir logar como o vendedor no teste.
- **Adiado (polish opcional):** HTMX pra enviar sem recarregar; marcar mensagens
  como `lida`/badge de não lidas; registrar `Conversa`/`Mensagem` no admin.
- ✅ **Git no ar (2026-07-08):** repo público em
  https://github.com/gabrielbastosg/desapega (branch `main`, 1º commit). O
  `.gitignore` foi corrigido (comentários estavam na mesma linha do padrão e
  deixavam `.env`/`db.sqlite3` fora do ignore) e criado `.env.example`. `.env`
  confirmado fora do versionamento.
- ⚠️ **Ambiente mudou:** o projeto agora roda no **venv** em
  `C:\Users\gabri\OneDrive\PC\Desktop\django-projetos\.venv` (não mais no Python
  global — o editor provavelmente criou/ativou sozinho). Pacotes do
  `requirements.txt` (django-storages, boto3, etc.) instalados **dentro do venv**
  em 2026-07-08. **Sempre usar esse venv daqui pra frente** e instalar pacotes lá.

## Fase 4 — máquina de estados (2026-07-08) ✅ testada ponta-a-ponta
- `views.py`: nova `mudar_situacao(request, pk)` — guarda de dono, só POST,
  valida `nova in dict(Anuncio.SITUACAO_CHOICES)` antes de salvar. Em
  `lista_anuncios`: esconde vendidos por padrão (`?vendidos=1` mostra), passa
  `ver_vendidos` no contexto.
- `urls.py`: `anuncio/<int:pk>/situacao/` name='mudar_situacao'.
- `detalhe.html`: painel do dono com botões contextuais por estado
  (disponível→reservado/vendido; reservado→vendido/voltar; vendido→reabrir),
  cada um num `<form method=post>` com csrf e `<button name=situacao value=...>`.
- `lista.html`: checkbox "Mostrar vendidos". `style.css`: `.dono-acoes`,
  `.situacao-botoes`, `.btn-reservar` (laranja), `.btn-vender` (verde),
  `.check-vendidos`.

## Fase 3 — busca/filtros (2026-07-08) ✅ testada ponta-a-ponta
- `views.py`: `lista_anuncios` agora lê filtros da query string (`q`, `categoria`
  por slug, `cidade` icontains, `preco_min/max`) + paginação (Paginator, 9/pág).
  Passa `querystring` (GET sem `page`) pros links de paginação. Imports novos:
  `Paginator`, `Q`, e `Categoria` no import de `.models`.
- `lista.html`: form GET de filtros (busca, select de categoria, cidade, faixa de
  preço, Filtrar/Limpar), grid com `{% empty %}`, e nav de paginação.
- `style.css`: blocos `.filtros` (flex horizontal, sobrescreve width:100% global) e
  `.paginacao`.
- Melhorias adiadas: `?preco_min=abc` na URL crasha (campos são type=number, pelo
  site não acontece) — blindar depois com form de filtro.

## Fase 2 — feita em 2026-07-07 ✅ (Fotos no S3)
- Bucket S3 **`desapega-media-gabrielbg`** (us-east-1), privado (Block Public
  Access ligado), SSE-S3. Usuário IAM **`desapega-app`** com política
  **`desapega-s3-policy`** restrita só a esse bucket (List/Get/Put/Delete).
- Credenciais no arquivo **`.env`** (na raiz, já no .gitignore): variáveis
  `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`.
- Pacotes: `django-storages`, `boto3`, `python-dotenv`, `Pillow`.
- `settings.py`: carrega `.env` com `load_dotenv`; bloco AWS S3 com
  `AWS_S3_SIGNATURE_VERSION='s3v4'`, `AWS_DEFAULT_ACL=None`,
  `AWS_QUERYSTRING_AUTH=True`, e `STORAGES['default']` = S3Storage.
- Model `Foto` (FK Anuncio `related_name='fotos'`, `ImageField(upload_to='anuncios/')`).
  Migration `0002_foto`. Admin com `FotoInline` no `AnuncioAdmin`.
- Upload funciona pelo admin **e** pelo site (form com `enctype` +
  `<input name="fotos" multiple>`; views `criar`/`editar` fazem
  `Foto.objects.create` sobre `request.FILES.getlist('fotos')`).
- Galeria exibida no `detalhe.html` (URLs assinadas). Testado ponta-a-ponta. OK.

### Pendências de higiene da Fase 2
- 🔐 **Rotacionar a chave IAM** — ✅ FEITO em 2026-07-07. Chave antiga (exposta,
  `AKIAWTXQ35DR7ETZUAVS`) excluída; nova chave no `.env` testada e funcionando.
- 🧹 **Limpar dados de teste** (ainda pendente): usuário `maria_teste`; anúncios
  "Bicicleta Caloi" e "Mesa de escritorio"; imagens de teste no bucket
  (`anuncios/teste_upload.png` e o print). Podem ser apagados pelo admin.

## Fase 1 — feita em 2026-07-07 ✅
- Models `Categoria` e `Anuncio` (campo de status chama-se **`situacao`**,
  não "estado", pra não confundir com UF). Migration `0001_initial` aplicada.
- Admin: `CategoriaAdmin` (com `prepopulated_fields` no slug) e `AnuncioAdmin`.
- Views (function-based) em `anuncios/views.py`: `lista_anuncios`,
  `detalhe_anuncio`, `criar_anuncio`, `editar_anuncio`, `apagar_anuncio`,
  `meus_anuncios`, `cadastro`. Guardas `@login_required` + checagem de dono.
- `anuncios/forms.py`: `AnuncioForm` (ModelForm; vendedor/situacao fora do form).
- Auth: `config/urls.py` inclui `django.contrib.auth.urls` em `/contas/`;
  `settings.py` com `LOGIN_URL`/`LOGIN_REDIRECT_URL`/`LOGOUT_REDIRECT_URL`.
- Templates em `anuncios/templates/` (Claude criou): base, lista, detalhe,
  form, confirmar_apagar, meus, cadastro e `registration/login.html`.
- Testado ponta-a-ponta (cadastro→login→criar; e bloqueio de não-dono). OK.
- Dados de teste no banco de dev: usuário `maria_teste` + anúncio "Bicicleta
  Caloi" (podem ser apagados).

## Fase 0 — feita em 2026-07-07 ✅
- Projeto Django `config` + app `anuncios` criados (Python 3.13, Django 5.2.8
  global, **sem venv** — usuário optou pelo Python global).
- `settings.py`: app `anuncios` registrado; `LANGUAGE_CODE='pt-br'`;
  `TIME_ZONE='America/Sao_Paulo'`.
- Migrations iniciais aplicadas (SQLite `db.sqlite3`); superusuário criado.
- `runserver` responde 200. `requirements.txt` criado (só Django; S3 na Fase 2).
- Git ainda **não** iniciado (usuário quer esperar ter mais conteúdo).
- Formato de trabalho: **usuário digita o código**; Claude orienta e confere.

## O que foi decidido nesta sessão
- Projeto novo escolhido: **Desapega** — marketplace de classificados.
  Motivo: fugir do padrão "explorer" (já feito 6x). Aqui o conteúdo é do
  usuário, tem upload de fotos, chat e máquina de estados.
- **Arquitetura:** Django full-stack (templates) primeiro; SQLite no dev.
  React + DRF fica como **fase opcional no fim** (padrão Mural HTML→React).
- **AWS:** só **S3** para as fotos (django-storages + boto3), dentro do
  "sempre grátis". Reaproveitar conta/travas do projeto `site_aws`.
- Plano completo escrito em `PLANO.md` (8 fases + modelo de dados + escopo MVP).

## Próximo passo
✅ CSS já foi extraído pro `anuncios/static/anuncios/style.css` (base.html limpo).

➡️ **Fase 3 — Busca e filtros:** busca por texto (título/descrição), filtro por
   categoria, cidade e faixa de preço, e paginação na home. Ver seção 5 do
   PLANO.md.

   Antes da Fase 3, se quiser, resolver as **pendências de higiene da Fase 2**
   (rotacionar chave IAM + limpar dados de teste — ver acima).

   Também pendente (quando quiser): `git init` + 1º commit (o `.gitignore`
   já está pronto na raiz).

## Decisões em aberto (ver seção 7 do PLANO.md)
- Nome do repositório (sugestão: `desapega`).
- Hospedagem no deploy (Render/Railway/Fly — decidir na Fase 7).
- SQLite vs Postgres no deploy.
- Fotos S3: bucket público no prefixo de mídia vs. URLs assinadas.
- Tema visual.

## Anotações / dúvidas
- **CSS (2026-07-09):** `style.css` foi refatorado com `:root` (variáveis de cor,
  espaçamento, raio, sombra) e mais respiro. Mesmas classes, mesmo tema índigo.
- 💡 **Ideia p/ próxima:** separar o CSS em vários arquivos (ex.: base/anuncios/
  chat) — o `:root` já deixa isso fácil (variáveis compartilhadas). Decidir entre
  vários `<link>` no base.html ou um arquivo que faz `@import` dos parciais.
- (anote aqui o que travou ou que queira perguntar na próxima sessão)
