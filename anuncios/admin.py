from django.contrib import admin
from .models import Categoria, Anuncio, Foto, Conversa, Mensagem, Favorito
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


class MensagemInline(admin.TabularInline):
    model = Mensagem
    extra = 0 # 0: não mostra campo em branco (aqui a gente só lê)


@admin.register(Conversa)
class ConversaAdmin(admin.ModelAdmin):
    list_display = ['anuncio','comprador','criado_em']
    list_filter = ['criado_em']
    search_fields = ['anuncio__titulo','comprador__username']
    inlines = [MensagemInline]   # as mensagens aparecem dentro da conversa


@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ['autor','conversa','texto','lida','criado_em']
    list_filter = ['lida','criado_em']
    search_fields = ['texto','autor__username']

@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ['usuario','anuncio','criado_em']
    search_fields = ['usuario__username','anuncio__titulo']
