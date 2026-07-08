from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Categoria(models.Model):
    nome = models.CharField(max_length=50,unique=True)
    # slug = versão "URL-friendly" do nome (ex.: "Áudio & TV" -> "audio-tv").
    # Vamos usar em links tipo /categoria/eletronicos/ mais pra frente.
    slug = models.SlugField(max_length=60,unique=True)

    class Meta:
        ordering = ['nome'] #lista em ordem alfabetica
        verbose_name_plural = 'Categorias' # nome Bonito no admin

    def __str__(self):
        return self.nome

class Anuncio(models.Model):
    # "choices" = lista fechada de valores. 1º item é o que vai no banco,
    # o 2º é o rótulo que aparece pro usuário.
    CONDICAO_CHOICES = [
        ('novo', 'Novo'),
        ('usado', 'Usado'),
    ]
    SITUACAO_CHOICES = [
        ('disponivel', 'Disponível'),
        ('reservado', 'Reservado'),
        ('vendido', 'Vendido'),
    ]

    titulo = models.CharField(max_length=120)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    condicao = models.CharField(max_length=10, choices=CONDICAO_CHOICES, default='usado')
    cidade = models.CharField(max_length=80)
    situacao = models.CharField(max_length=12, choices=SITUACAO_CHOICES, default='disponivel')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='anuncios')
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='anuncios')
   # Datas automáticas:
    criado_em = models.DateTimeField(auto_now_add=True)      # só na criação
    atualizado_em = models.DateTimeField(auto_now=True)      # a cada save   

    class Meta:
        ordering = ['-criado_em'] # Mais recentes primeiro

    def __str__(self):
        return self.titulo      

class Foto(models.Model):
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE, related_name='fotos')
    # ImageField salva no S3 (por causa do STORAGES no settings).
    # upload_to='anuncios/' = as fotos ficam no "prefixo" anuncios/ do bucket.
    imagem = models.ImageField(upload_to='anuncios/')
    ordem = models.PositiveIntegerField(default=0)  # p/ ordenar as fotos
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordem', 'id']

    def __str__(self):
        return f'Foto de {self.anuncio.titulo}'   