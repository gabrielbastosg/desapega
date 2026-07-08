from django import forms
from .models import Anuncio


class AnuncioForm(forms.ModelForm):
    class Meta:
        model = Anuncio
        # Só os campos que o usuário preenche. O "vendedor" a gente
        # define sozinho (= usuário logado) e "situacao" fica no padrão.
        fields = ['titulo', 'descricao', 'preco', 'condicao', 'cidade', 'categoria']