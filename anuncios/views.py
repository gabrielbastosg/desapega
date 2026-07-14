from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Anuncio, Foto, Categoria, Conversa, Mensagem, Favorito
from .forms import AnuncioForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
# Create your views here.
def lista_anuncios(request):
    anuncios = Anuncio.objects.select_related('categoria', 'vendedor').all()
    # --- esconder vendidos por padrão (?vendidos=1 mostra eles) ---
    ver_vendidos = request.GET.get('vendidos') == '1'
    if not ver_vendidos:
        anuncios = anuncios.exclude(situacao='vendido')
    # --- filtros (vêm da query string, ex.: ?q=violao&cidade=Recife) ---
    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria','').strip()
    cidade = request.GET.get('cidade','').strip()
    preco_min = request.GET.get('preco_min','').strip()
    preco_max = request.GET.get('preco_max','').strip()

    if q:
        # Q(...) permite "OU": bate no título OU na descrição
        anuncios = anuncios.filter(Q(titulo__icontains=q) | Q(descricao__icontains=q))
    if categoria:
        anuncios = anuncios.filter(categoria__slug=categoria)
    if cidade:
        anuncios = anuncios.filter(cidade__icontains=cidade)
    if preco_min:
        anuncios = anuncios.filter(preco__gte=preco_min)
    if preco_max:
        anuncios = anuncios.filter(preco__lte=preco_max)

    # --- paginação: 9 anúncios por página ---
    paginator = Paginator(anuncios, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    # querystring dos filtros SEM o 'page' (pros links "anterior/próxima")
    params = request.GET.copy()
    params.pop('page', None)

    contexto = {
        'anuncios': page_obj,          # page_obj já é iterável como uma lista
        'page_obj': page_obj,
        'categorias': Categoria.objects.all(),
        'querystring': params.urlencode(),
        # valores atuais, pra reencher o formulário depois de buscar:
        'q': q,
        'categoria_sel': categoria,
        'cidade': cidade,
        'preco_min': preco_min,
        'preco_max': preco_max,
        'ver_vendidos': ver_vendidos,
    }
    return render(request, 'anuncios/lista.html', contexto)        

def detalhe_anuncio(request, pk):
    anuncio = get_object_or_404(Anuncio, pk=pk)
    # o usuário logado já favoritou este anúncio? (anônimo nunca favoritou)
    ja_favoritou = (
        request.user.is_authenticated
        and Favorito.objects.filter(usuario=request.user, anuncio=anuncio).exists()
    )
    return render(request, 'anuncios/detalhe.html', {
        'anuncio': anuncio,
        'ja_favoritou': ja_favoritou,
    })


@login_required
def criar_anuncio(request):
    if request.method == 'POST':
        form = AnuncioForm(request.POST)
        if form.is_valid():
            anuncio = form.save(commit=False)   # cria o objeto mas não salva ainda
            anuncio.vendedor = request.user      # define o dono = quem está logado
            anuncio.save()
            for imagem in request.FILES.getlist('fotos'):
                Foto.objects.create(anuncio=anuncio, imagem=imagem)
            return redirect('anuncios:detalhe', pk=anuncio.pk)
    else:
        form = AnuncioForm()
    return render(request, 'anuncios/form.html',
                  {'form': form, 'titulo_pagina': 'Novo anúncio'})


@login_required
def editar_anuncio(request, pk):
    anuncio = get_object_or_404(Anuncio, pk=pk)
    if anuncio.vendedor != request.user:         # só o dono edita
        return redirect('anuncios:detalhe', pk=anuncio.pk)
    if request.method == 'POST':
        form = AnuncioForm(request.POST, instance=anuncio)
        if form.is_valid():
            form.save()
            for imagem in request.FILES.getlist('fotos'):
                Foto.objects.create(anuncio=anuncio, imagem=imagem)
            return redirect('anuncios:detalhe', pk=anuncio.pk)
    else:
        form = AnuncioForm(instance=anuncio)
    return render(request, 'anuncios/form.html',
                  {'form': form, 'titulo_pagina': 'Editar anúncio'})


@login_required
def apagar_anuncio(request, pk):
    anuncio = get_object_or_404(Anuncio, pk=pk)
    if anuncio.vendedor != request.user:         # só o dono apaga
        return redirect('anuncios:detalhe', pk=anuncio.pk)
    if request.method == 'POST':
        anuncio.delete()
        return redirect('anuncios:meus')
    return render(request, 'anuncios/confirmar_apagar.html', {'anuncio': anuncio})


@login_required
def meus_anuncios(request):
    anuncios = request.user.anuncios.select_related('categoria').all()
    return render(request, 'anuncios/meus.html', {'anuncios': anuncios})


def cadastro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)                 # já loga após cadastrar
            return redirect('anuncios:lista')
    else:
        form = UserCreationForm()
    return render(request, 'anuncios/cadastro.html', {'form': form})

@login_required
def mudar_situacao(request, pk):
    anuncio = get_object_or_404(Anuncio, pk=pk)
    if anuncio.vendedor != request.user:          # só o dono muda o estado
        return redirect('anuncios:detalhe', pk=anuncio.pk)
    if request.method == 'POST':
        nova = request.POST.get('situacao')
        # só aceita um dos valores válidos do choices (blindagem)
        if nova in dict(Anuncio.SITUACAO_CHOICES):
            anuncio.situacao = nova
            anuncio.save()
    return redirect('anuncios:detalhe', pk=anuncio.pk)

@login_required
def iniciar_conversa(request, pk):
    anuncio = get_object_or_404(Anuncio, pk=pk)
    # o dono não conversa consigo mesmo
    if anuncio.vendedor == request.user:
        return redirect('anuncios:detalhe', pk=anuncio.pk)
    # cria a conversa se ainda não existe; senão, reusa a que já existe
    conversa, criada = Conversa.objects.get_or_create(
        anuncio=anuncio, comprador=request.user
    )
    return redirect('anuncios:conversa', pk=conversa.pk)


@login_required
def detalhe_conversa(request, pk):
    conversa = get_object_or_404(Conversa, pk=pk)
    # só o comprador e o vendedor do anúncio podem abrir esta conversa
    if request.user != conversa.comprador and request.user != conversa.anuncio.vendedor:
        return redirect('anuncios:lista')
    if request.method == 'POST':
        texto = request.POST.get('texto', '').strip()
        if texto:                             # ignora mensagem vazia
            Mensagem.objects.create(conversa=conversa, autor=request.user, texto=texto)
        return redirect('anuncios:conversa', pk=conversa.pk)   # PRG: evita reenvio no F5
    conversa.mensagens.filter(lida=False).exclude(autor=request.user).update(lida=True)
    return render(request, 'anuncios/conversa.html', {'conversa': conversa})


@login_required
def minhas_conversas(request):
    # conversas em que EU sou o comprador
    como_comprador = Conversa.objects.filter(
        comprador=request.user
    ).select_related('anuncio', 'anuncio__vendedor')
    # conversas em que EU sou o vendedor (nos meus anúncios)
    como_vendedor = Conversa.objects.filter(
        anuncio__vendedor=request.user
    ).select_related('anuncio', 'comprador')
    return render(request, 'anuncios/inbox.html', {
        'como_comprador': como_comprador,
        'como_vendedor': como_vendedor,
    })

@login_required
def favoritar(request, pk):
    anuncio = get_object_or_404(Anuncio, pk=pk)
    if request.method == 'POST':
        # get_or_create devolve (objeto, criado?). Se já existia, o clique desfavorita.
        favorito, criado = Favorito.objects.get_or_create(
            usuario=request.user, anuncio=anuncio
        )
        if not criado:
            favorito.delete()
    # volta pra página de onde veio (o template manda em 'next'); senão, o detalhe
    destino = request.POST.get('next')
    if destino:
        return redirect(destino)
    return redirect('anuncios:detalhe', pk=anuncio.pk)


@login_required
def meus_favoritos(request):
    favoritos = Favorito.objects.filter(usuario=request.user).select_related(
        'anuncio', 'anuncio__categoria', 'anuncio__vendedor'
    )
    return render(request, 'anuncios/favoritos.html', {'favoritos': favoritos})


def perfil_publico(request, username):
    # busca o vendedor pelo username da URL (404 se não existir)
    vendedor = get_object_or_404(User, username=username)
    # mostra só os anúncios ativos dele (esconde os vendidos), mais recentes primeiro
    anuncios = vendedor.anuncios.exclude(situacao='vendido').select_related('categoria')
    return render(request, 'anuncios/perfil.html', {
        'vendedor': vendedor,
        'anuncios': anuncios,
    })