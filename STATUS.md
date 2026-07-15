# STATUS — onde paramos (Desapega)

> Atualize ao fim de cada sessão. É o primeiro lugar a ler quando voltar.

## Sessão atual
- **Data:** 2026-07-15
- **Fase atual:** FASES 0 a 6 CONCLUÍDAS ✅. (Deploy/Fase 7: usuário decidiu NÃO fazer.)
  Nesta sessão: **HTMX no chat** — enviar mensagem sem recarregar a página (1º HTMX do projeto).

## HTMX no chat (2026-07-15) ✅ testado no navegador
- **Objetivo:** enviar mensagem sem reload; melhoria progressiva (sem JS, cai no PRG antigo).
- **`base.html`:** carrega `https://unpkg.com/htmx.org@2.0.4` no `<head>`; novo
  `{% block scripts %}{% endblock %}` antes do `</body>` (pra páginas injetarem JS próprio).
- **NOVO `_mensagem.html`** (partial): a bolha da mensagem (`.msg/.msg-bolha/.msg-info`),
  extraída do `conversa.html` pra ter o HTML num lugar só (usado na lista E na resposta HTMX).
- **`conversa.html`:** thread virou `<div class="chat-thread" id="chat-thread">` com
  `{% include 'anuncios/_mensagem.html' %}` no loop; form ganhou
  `hx-post="{% url 'anuncios:conversa' conversa.pk %}"`, `hx-target="#chat-thread"`,
  `hx-swap="beforeend"` (o `{% csrf_token %}` continua dentro → HTMX envia junto). Novo
  `{% block scripts %}` com listener `htmx:afterSwap`: remove o `.vazio`, dá `form.reset()`,
  foca o textarea e rola pro fim.
- **`views.py` (`detalhe_conversa`):** no POST, guarda a msg criada em `mensagem`; se
  `request.headers.get('HX-Request')`, retorna `render(..., '_mensagem.html', {'m': mensagem})`
  (só a bolha); senão, `redirect` (PRG) como antes. ⚠️ Cuidado que pegou: a linha que marca
  msgs como lidas (`...filter(lida=False).exclude(autor=request.user).update(lida=True)`)
  saiu sem querer ao trocar o bloco; foi restaurada (fica no caminho GET, antes do render).
- Testado: `manage.py check` OK; no navegador as bolhas aparecem na hora, sem reload. OK.
- **Ainda adiado do chat:** registrar Conversa/Mensagem no admin.

## Sessão anterior (2026-07-14)
- **Badge de mensagens não lidas** (usa o campo `lida` que já existia).

## Badge de mensagens não lidas (2026-07-14) ✅ testado no navegador
- **Sem migração** — o campo `Mensagem.lida` (BooleanField default False) já existia.
- **Marcar como lida** (`views.py`, `detalhe_conversa`): antes do `return render` final
  (só roda no GET, pois o POST dá return antes), `conversa.mensagens.filter(lida=False)
  .exclude(autor=request.user).update(lida=True)`. Ao abrir a thread, as msgs que o OUTRO
  mandou viram lidas.
- **Contador global** — NOVO arquivo `anuncios/context_processors.py` com
  `mensagens_nao_lidas(request)`: se anônimo, `{}`; senão conta `Mensagem` com `lida=False`,
  `.exclude(autor=request.user)`, em conversas onde sou comprador OU vendedor
  (`Q(conversa__comprador=request.user) | Q(conversa__anuncio__vendedor=request.user)`).
  Devolve `{'nao_lidas': total}`. Registrado no `settings.py` (TEMPLATES → context_processors).
- **Template** (`base.html`): link "Conversas" ganhou
  `{% if nao_lidas %}<span class="badge-nao-lidas">{{ nao_lidas }}</span>{% endif %}`
  (a bolinha só aparece quando > 0).
- **CSS** (`base.css`): `.badge-nao-lidas` — bolinha vermelha (#e11d48) arredondada.
- Testado: `manage.py check` OK; shell mostra gabri e maria com 1 não lida cada (2 msgs no
  banco). No navegador: bolinha aparece com o nº e SOME ao abrir a conversa. OK pelo usuário.
- **Ainda "adiado" do chat:** HTMX (enviar sem reload); registrar Conversa/Mensagem no admin.

## Polish de UI (2026-07-13) ✅ testado
- **Modo escuro com botão 🌙/☀️** — primeiro JavaScript do projeto.
  - `base.css`: o tema deixou de depender só do sistema. Agora usa
    `:root[data-theme="dark"]` (e `[data-theme="light"]`), que sobrescrevem as
    variáveis de cor. Cada bloco define também `color-scheme` (light/dark) pros
    controles nativos. Removido o antigo `@media (prefers-color-scheme: dark)`
    e o `color-scheme: light dark` do `:root`. Nova classe `.btn-tema`.
  - `base.html`: (1) script inline no `<head>` define o tema inicial ANTES de
    pintar (escolha salva no `localStorage` OU preferência do sistema na 1ª
    visita) — evita "piscar" a cor errada; (2) botão `#btn-tema` no `<nav>`
    (visível logado ou não); (3) script no fim do `<body>` alterna o tema,
    grava no `localStorage` e troca o ícone (☀️ quando escuro, 🌙 quando claro).
  - Testado: alterna na hora, lembra da escolha ao recarregar. OK pelo usuário.
- **Header fixo** — `header` ganhou `position: sticky; top:0; z-index:100` +
  sombra. (Usuário notou que com pouco conteúdo ele quase não aparece, mas é
  inofensivo e passa a ajudar quando a home encher; ficou mantido.)
- **Estado vazio da home** — `lista.html`: o `{% empty %}` virou uma caixa com
  ícone 🔍, título e botão de anunciar (contextual: logado → criar; anônimo →
  cadastro). `base.css`: `.vazio` agora é uma caixa pontilhada com
  `grid-column: 1/-1` (ocupa a largura toda no grid) + classes `.vazio-icone` e
  `.vazio-titulo`. Vale pra todos os "vazios" do site (consistência).
- **Não commitado ainda** — mudanças só no disco; `git` local ainda sem commit
  desse polish.

## Sessão anterior (2026-07-10)
- Refatoramos o CSS e fizemos a Fase 6 inteira (favoritos + perfil).

## Fase 6 — favoritos + perfil público (2026-07-10) ✅ testada
- **Model** (`models.py`): `Favorito` (usuario FK related_name='favoritos',
  anuncio FK related_name='favoritado_por', criado_em;
  `unique_together=('usuario','anuncio')`, ordering `-criado_em`).
  Migration `0004_favorito` aplicada.
- **Views** (`views.py`): `favoritar(pk)` (só POST, `@login_required`, toggle via
  `get_or_create`+`delete`; volta pelo `next` do POST ou pro detalhe);
  `meus_favoritos` (lista com select_related); `detalhe_anuncio` agora passa
  `ja_favoritou`; `perfil_publico(username)` (sem login; `get_object_or_404(User)`;
  anúncios não-vendidos do vendedor). Imports novos: `Favorito`, `User`.
- **URLs**: `anuncio/<pk>/favoritar/`, `favoritos/`, `u/<username>/` (name='perfil').
- **Templates** (Claude criou/editou): `favoritos.html` (grade de cards);
  `perfil.html` (cabeçalho com avatar-inicial + data de cadastro + nº de anúncios,
  e grade dos anúncios ativos). Editados: `detalhe.html` (botão ❤️ Favoritar/
  Favoritado num form POST com hidden `next`; nome do vendedor virou link pro
  perfil) e `base.html` (link "Favoritos" no menu).
- **CSS** (`anuncios.css`): seções 8 (`.acoes-anuncio`, `.btn-favorito` +
  `.favoritado`) e 9 (`.perfil-topo`, `.perfil-avatar`, `.perfil-nome`,
  `.perfil-secao`).
- **Testes automatizados** (test client): toggle favorita→True / clica de novo→
  False; `/favoritos/` logado 200 e anônimo 302; `/u/<user>/` 200, inexistente
  404; detalhe traz o link pro perfil. Todos OK.
- **Falta teste visual no navegador** (usuário faz): logar, favoritar num anúncio
  de OUTRO usuário (o dono não vê o botão, é de propósito), ver em "Favoritos",
  desfavoritar, e abrir o perfil pelo nome do vendedor.

## CSS — refatorado e separado (2026-07-10) ✅
- O `style.css` único (230 linhas, tudo misturado) foi **dividido em 3 arquivos**
  em `anuncios/static/anuncios/css/`:
  - **`base.css`** — variáveis `:root`, reset, tipografia, cabeçalho/menu, layout
    `.container`, botões (`.btn*`), formulários e utilitários (`.voltar`, `.vazio`).
    Carrega **primeiro** (tem as variáveis que os outros usam).
  - **`anuncios.css`** — grid, cards, `.preco/.meta`, badges de situação, galeria,
    filtros, paginação e ações do dono (`.dono-acoes` etc.).
  - **`chat.css`** — `.chat-*`, `.msg*`, inbox (`.inbox-secao`, `.conversa-item`).
- `base.html`: um `<link>` virou **três** (base → anuncios → chat, nessa ordem).
- Também deixamos mais legível: 1 propriedade por linha nas regras densas, sem
  mudar nenhuma cor/valor — visual idêntico. `style.css` antigo apagado.
- Testado: home + os 3 CSS respondem 200, sem erros no runserver.
- Escolha: 3 `<link>` (mais simples/explícito que `@import`, cada arquivo cacheia
  sozinho). Fecha a "💡 Ideia p/ próxima" que estava anotada nas Anotações.

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
- ✅ **Feito (2026-07-10):** CSS separado em base/anuncios/chat com 3 `<link>`.
  Ver seção "CSS — refatorado e separado" no topo.
- (anote aqui o que travou ou que queira perguntar na próxima sessão)
