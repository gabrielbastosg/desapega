from django.contrib import admin
from .models import Categoria, Anuncio, Foto
# Register your models here.

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug']
    search_fields = ['nome']
    # Preenche o slug automaticamente enquanto você digita o nome:
    prepopulated_fields = {'slug': ('nome',)}

class FotoInline(admin.TabularInline):
    model = Foto
    extra = 1   # mostra 1 campo de foto em branco pronto pra enviar

@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
    # Colunas que aparecem na listagem do admin:
    list_display = ['titulo', 'preco', 'categoria', 'situacao', 'vendedor', 'criado_em']
    # Filtros na barra lateral direita:
    list_filter = ['situacao', 'condicao', 'categoria']
    # Caixa de busca (busca por título e cidade):
    search_fields = ['titulo', 'descricao', 'cidade']
    inlines = [FotoInline]  # mostra as fotos do anúncio na mesma página do admin