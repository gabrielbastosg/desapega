# Desapega — Marketplace de Classificados (plano de estudos)

> Projeto novo, **maior e diferente** dos "explorers". Aqui o conteúdo é criado
> pelos usuários (não vem de API externa), tem upload de fotos, chat entre
> pessoas e um fluxo com estados. Django é o centro; a AWS entra só como tempero (S3).
>
> `STATUS.md` sempre indica onde paramos. Este arquivo é o roteiro completo.

---

## 1. O que é o app (visão)

Um site de classificados estilo "Desapega/OLX-lite":

- Qualquer visitante **navega e busca** anúncios (itens à venda).
- Usuário logado **cria anúncios** com título, descrição, preço, categoria,
  cidade e **fotos**.
- O dono marca o item como **disponível → reservado → vendido**.
- Interessado e vendedor **conversam por um chat** dentro do anúncio.
- Cada usuário tem **"Meus anúncios"** e um **perfil público**.

Por que este projeto ensina coisas novas (vs. os explorers):
- **Conteúdo gerado pelo usuário** (não é só exibir dados de fora).
- **Upload de mídia** → primeira vez usando **S3** de verdade.
- **Relações entre usuários** (chat comprador ↔ vendedor).
- **Máquina de estados** com regras de permissão (só o dono muda o estado).

---

## 2. Decisões de arquitetura

- **Backend:** Django (full-stack, com templates). Banco **SQLite** no
  desenvolvimento (zero configuração); Postgres fica para o deploy, se rolar.
- **Frontend:** templates Django + CSS + um pouco de JS/HTMX para as partes
  interativas (preview de foto antes de enviar, chat sem recarregar a página).
- **Fotos:** armazenadas no **AWS S3** via `django-storages` + `boto3`
  (dentro do "sempre grátis": 5 GB, 20k GET, 2k PUT por mês).
- **React:** **fase opcional no fim.** Expor uma API (DRF) e construir um front
  React que consome — mesmo padrão que já fizemos (Mural HTML → Mural React).
  Deixado por último de propósito para não dobrar a complexidade cedo demais.

> Por que templates primeiro? A parte nova/difícil aqui é o domínio (S3, chat,
> estados). Templates deixam focar no Django e entregar rápido. React+DRF você
> já provou no `mural-fullstack`, então vira consolidação depois.

---

## 3. Modelo de dados (rascunho)

```
User (auth padrão do Django)
 └─ Profile (1:1)  → avatar, cidade, whatsapp, bio

Categoria           → nome, slug            (ex.: Eletrônicos, Móveis, Roupas)

Anuncio             → titulo, descricao, preco, condicao (novo/usado),
                      cidade, estado (disponivel/reservado/vendido),
                      categoria (FK), vendedor (FK User),
                      criado_em, atualizado_em
 └─ Foto (N)        → anuncio (FK), arquivo (no S3), ordem

Conversa            → anuncio (FK), comprador (FK User), vendedor (FK User)
 └─ Mensagem (N)    → conversa (FK), autor (FK User), texto, criado_em, lida

Favorito            → usuario (FK), anuncio (FK)   (opcional — já é familiar)
```

Observações:
- Um anúncio tem **várias fotos** (relação 1:N `Anuncio → Foto`).
- Uma **conversa** é única por (anúncio + comprador); as mensagens penduram nela.
- O `estado` do anúncio é a máquina de estados: só o **vendedor** pode mudar.

---

## 4. Escopo do MVP (o "mínimo que já é um produto")

Ordem sugerida, do essencial ao "bom ter":

**MVP (precisa ter):**
1. Cadastro / login / logout (auth do Django).
2. Criar anúncio (sem fotos ainda) — título, descrição, preço, categoria, cidade.
3. Listar anúncios (home) + página de detalhe.
4. Editar / apagar anúncio (só o dono).
5. "Meus anúncios".
6. **Fotos no S3** (upload de 1..N imagens por anúncio).
7. Busca e filtros (texto, categoria, cidade, faixa de preço).
8. Estados: marcar reservado / vendido (só o dono), com badge visual.

**Fase 2 (o que dá alma ao app):**
9. Chat comprador ↔ vendedor (conversas + mensagens).
10. Favoritos (❤️ salvar anúncio).
11. Perfil público do vendedor (foto, cidade, anúncios ativos).

**Depois / opcional:**
12. Notificações por e-mail (ex.: "alguém te mandou mensagem").
13. Deploy (decidir hospedagem — ver seção 6).
14. Expor API DRF + frontend React (consolidação).

---

## 5. Roadmap por fases (com objetivo claro em cada uma)

### Fase 0 — Esqueleto do projeto
Criar repo, ambiente virtual, projeto Django, app `anuncios`, `settings`
básicos, admin ligado. Rodar `runserver` e ver a página inicial. SQLite local.

### Fase 1 — Anúncios CRUD (sem foto)
Models `Categoria` e `Anuncio`, migrations, formulário de criar/editar,
listagem, detalhe, apagar. Auth (login obrigatório para criar). "Meus anúncios".
**Entrega:** dá pra cadastrar e navegar anúncios de texto.

### Fase 2 — Fotos no S3
Criar bucket S3 (região us-east-1, mesmas travas de custo). Configurar
`django-storages` + `boto3` + credenciais IAM (usuário só com acesso ao bucket).
Model `Foto`, upload múltiplo, exibir no detalhe.
**Entrega:** anúncio com galeria de fotos servidas do S3.

### Fase 3 — Busca e filtros
Busca por texto (título/descrição), filtro por categoria, cidade e faixa de
preço. Paginação. **Entrega:** dá pra achar coisas no meio de muitos anúncios.

### Fase 4 — Máquina de estados
`estado` do anúncio (disponível/reservado/vendido), botões só para o dono,
badges na listagem e no detalhe, esconder vendidos por padrão (com opção de ver).
**Entrega:** o ciclo de vida do anúncio funciona.

### Fase 5 — Chat entre usuários
Models `Conversa` e `Mensagem`, iniciar conversa a partir do anúncio, caixa de
entrada ("Minhas conversas"), enviar/listar mensagens (HTMX para não recarregar).
**Entrega:** comprador e vendedor conversam dentro do app.

### Fase 6 — Favoritos + perfil público
❤️ favoritar, página "Meus favoritos", perfil público do vendedor.
**Entrega:** o app fica "social" e navegável.

### Fase 7 — Deploy + polish
Escolher hospedagem barata para o Django, variáveis de ambiente, `DEBUG=False`,
arquivos estáticos, Postgres (se aplicável). Ajustes visuais.
**Entrega:** app no ar em URL pública.

### Fase 8 — (opcional) API DRF + React
Expor endpoints REST e construir um frontend React que consome — consolidando o
que já fizemos no `mural-fullstack`.

---

## 6. AWS e travas de custo (revisar em toda sessão)

- **Único serviço AWS: S3** (fotos). Free tier: 5 GB, 20k GET, 2k PUT/mês.
- Reaproveitar a conta AWS e as travas do projeto `site_aws`:
  Free Plan, Budget de US$1 com alerta, região **us-east-1**.
- **Usuário IAM dedicado** com política restrita **só a este bucket** (não usar
  credenciais amplas).
- **Nunca** criar EC2, RDS, NAT ou nada "sempre ligado".
- **Django em si roda local** durante o desenvolvimento — sem custo.
- No deploy (Fase 7): preferir hospedagem gratuita de app (ex.: Render/Railway/
  Fly free tier) em vez de EC2, para não sair do custo zero. Decidir na hora.

---

## 7. Decisões em aberto (para revisar na próxima sessão)

- Nome/URL do repositório no GitHub (sugestão: `desapega`).
- Onde hospedar o Django no deploy (Render? Railway? decidir na Fase 7).
- Postgres no deploy vs. seguir com SQLite por mais tempo.
- Servir fotos do S3: bucket público só no prefixo de mídia **ou** URLs
  assinadas (presigned). Decidir na Fase 2 (começa simples).
- Tema visual / paleta do site.
