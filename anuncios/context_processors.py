from django.db.models import Q
from .models import Mensagem


def mensagens_nao_lidas(request):
    """Deixa 'nao_lidas' disponível em TODOS os templates (pro badge no menu)."""
    if not request.user.is_authenticated:
        return {}
    total = (
        Mensagem.objects
        .filter(
            Q(conversa__comprador=request.user)          # conversas onde sou comprador
            | Q(conversa__anuncio__vendedor=request.user),  # ou vendedor
            lida=False,
        )
        .exclude(autor=request.user)                     # não conta o que eu mesmo mandei
        .count()
    )
    return {'nao_lidas': total}