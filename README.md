# 🛍️ Desapega — Marketplace de Classificados

Um marketplace de classificados no estilo "OLX-lite", onde qualquer pessoa navega
e busca anúncios, e usuários cadastrados publicam seus próprios itens à venda com
fotos, e controlam o ciclo de vida do anúncio (disponível → reservado → vendido).

Projeto de estudo focado em **conteúdo gerado pelo usuário**, **upload de mídia na
nuvem** e **regras de permissão** — indo além do padrão "consumir uma API externa".

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.2-092E20)
![AWS S3](https://img.shields.io/badge/AWS-S3-FF9900)
![SQLite](https://img.shields.io/badge/DB-SQLite-003B57)

---

## ✨ Funcionalidades

- 🔐 **Autenticação** — cadastro, login e logout (auth nativo do Django).
- 📝 **CRUD de anúncios** — criar, editar e apagar, com **proteção de dono**
  (só quem publicou pode alterar).
- 🗂️ **"Meus anúncios"** — cada usuário vê e gerencia os seus.
- 📷 **Fotos na nuvem (AWS S3)** — upload de múltiplas imagens por anúncio,
  servidas via **URLs assinadas** (bucket privado).
- 🔎 **Busca e filtros** — por texto (título/descrição), categoria, cidade e
  faixa de preço, com **paginação**.
- 🏷️ **Máquina de estados** — o dono marca o anúncio como *disponível*,
  *reservado* ou *vendido*, com badges visuais; vendidos ficam escondidos da
  home por padrão (com opção de mostrar).

### 🚧 No roadmap
Chat comprador ↔ vendedor · Favoritos · Perfil público do vendedor · Deploy ·
API REST (DRF) + frontend React.

---

## 🛠️ Tecnologias

| Camada        | Ferramenta                                        |
|---------------|---------------------------------------------------|
| Backend       | Python 3.13, Django 5.2                           |
| Banco (dev)   | SQLite                                            |
| Mídia         | AWS S3 (`django-storages` + `boto3`), URLs assinadas |
| Frontend      | Templates Django + CSS                            |
| Config        | `python-dotenv` (variáveis de ambiente via `.env`) |

---

## 🚀 Como rodar localmente

**Pré-requisitos:** Python 3.13+ e uma conta AWS com um bucket S3 (para as fotos).

```bash
# 1. Clonar o repositório
git clone https://github.com/gabrielbastosg/desapega.git
cd desapega

# 2. Criar e ativar um ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Configurar as variáveis de ambiente
# Copie o modelo e preencha com suas credenciais AWS:
copy .env.example .env      # Windows
# cp .env.example .env      # Linux/Mac

# 5. Preparar o banco e criar um usuário admin
python manage.py migrate
python manage.py createsuperuser

# 6. Rodar o servidor
python manage.py runserver
```

Acesse **http://127.0.0.1:8000/** — e o admin em **/admin/**.

> ⚠️ As credenciais AWS ficam **apenas** no `.env` (que **nunca** vai para o Git).
> Use o `.env.example` como referência do que preencher.

---

## 📸 Screenshots

_(em breve)_

---

## 📁 Estrutura do projeto

```
desapega/
├── config/            # projeto Django (settings, urls, wsgi)
├── anuncios/          # app principal
│   ├── models.py      # Categoria, Anuncio, Foto
│   ├── views.py       # CRUD, busca/filtros, máquina de estados
│   ├── forms.py       # formulário de anúncio
│   ├── urls.py
│   ├── templates/     # HTML (base, lista, detalhe, forms, auth)
│   └── static/        # CSS
├── requirements.txt
├── .env.example       # modelo das variáveis de ambiente
└── manage.py
```

---

## 📚 Sobre

Projeto de portfólio construído para praticar Django full-stack e integração com
serviços de nuvem (AWS S3), com atenção a boas práticas de segurança (credenciais
fora do código, bucket privado, usuário IAM com permissão mínima).
