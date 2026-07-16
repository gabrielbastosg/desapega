from django import forms
from .models import Anuncio


class AnuncioForm(forms.ModelForm):
    class Meta:
        model = Anuncio
        # Só os campos que o usuário preenche. O "vendedor" a gente
        # define sozinho (= usuário logado) e "situacao" fica no padrão.
        fields = ['titulo', 'descricao', 'preco', 'condicao', 'cidade', 'categoria']

class FiltroForm(forms.Form):
    """Valida os filtros que vêm da query string (?q=...&preco_min=...)."""
    q = forms.CharField(required=False)
    categoria = forms.CharField(required=False)
    cidade = forms.CharField(required=False)
    preco_min = forms.DecimalField(required=False, min_value=0)
    preco_max = forms.DecimalField(required=False, min_value=0)