from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Anuncio, Foto, Categoria
from .forms import AnuncioForm
from django.core.paginator import Paginator
from django.db.models import Q
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
    return render(request, 'anuncios/detalhe.html', {'anuncio': anuncio})


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