from django.urls import path
from . import views

app_name = 'anuncios'

urlpatterns = [
    path('', views.lista_anuncios, name='lista'),
    path('anuncio/novo/', views.criar_anuncio, name='criar'),
    path('anuncio/<int:pk>/', views.detalhe_anuncio, name='detalhe'),
    path('anuncio/<int:pk>/editar/', views.editar_anuncio, name='editar'),
    path('anuncio/<int:pk>/apagar/', views.apagar_anuncio, name='apagar'),
    path('meus/', views.meus_anuncios, name='meus'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('anuncio/<int:pk>/situacao/', views.mudar_situacao, name='mudar_situacao'),
    path('conversas/', views.minhas_conversas, name='minhas_conversas'),
    path('anuncio/<int:pk>/conversar/', views.iniciar_conversa, name='iniciar_conversa'),
    path('conversa/<int:pk>/', views.detalhe_conversa, name='conversa'),
]