from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Anuncio, Categoria


class FiltrosTest(TestCase):
    """A home não pode quebrar com lixo na query string (?preco_min=abc)."""

    @classmethod
    def setUpTestData(cls):
        cls.vendedor = User.objects.create_user('vendedor', password='x')
        cls.cat = Categoria.objects.create(nome='Bikes', slug='bikes')
        cls.barato = Anuncio.objects.create(
            titulo='Bicicleta Caloi', descricao='aro 29', preco=Decimal('500'),
            cidade='Recife', categoria=cls.cat, vendedor=cls.vendedor,
        )
        cls.caro = Anuncio.objects.create(
            titulo='Mesa de escritorio', descricao='mdf', preco=Decimal('2000'),
            cidade='Olinda', categoria=cls.cat, vendedor=cls.vendedor,
        )

    def test_home_abre_sem_filtro(self):
        r = self.client.get(reverse('anuncios:lista'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context['anuncios']), 2)

    def test_preco_min_invalido_nao_quebra(self):
        r = self.client.get(reverse('anuncios:lista'), {'preco_min': 'abc'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context['anuncios']), 2)   # filtro ruim é ignorado
        self.assertEqual(r.context['preco_min'], '')      # e não vira "None" no form

    def test_preco_invalido_nao_derruba_os_outros_filtros(self):
        r = self.client.get(reverse('anuncios:lista'),
                            {'preco_min': 'abc', 'q': 'Caloi'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(list(r.context['anuncios']), [self.barato])
        self.assertEqual(r.context['q'], 'Caloi')

    def test_preco_negativo_e_ignorado(self):
        r = self.client.get(reverse('anuncios:lista'), {'preco_min': '-5'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context['anuncios']), 2)

    def test_filtro_de_preco_valido_continua_funcionando(self):
        r = self.client.get(reverse('anuncios:lista'), {'preco_min': '1000'})
        self.assertEqual(list(r.context['anuncios']), [self.caro])

    def test_busca_por_texto_bate_no_titulo_e_na_descricao(self):
        r = self.client.get(reverse('anuncios:lista'), {'q': 'aro 29'})
        self.assertEqual(list(r.context['anuncios']), [self.barato])

    def test_vendidos_ficam_escondidos_por_padrao(self):
        self.caro.situacao = 'vendido'
        self.caro.save()
        r = self.client.get(reverse('anuncios:lista'))
        self.assertEqual(list(r.context['anuncios']), [self.barato])
        r = self.client.get(reverse('anuncios:lista'), {'vendidos': '1'})
        self.assertEqual(len(r.context['anuncios']), 2)


class GuardaDeDonoTest(TestCase):
    """Só o dono edita, apaga ou muda a situação do próprio anúncio."""

    @classmethod
    def setUpTestData(cls):
        cls.dono = User.objects.create_user('dono', password='segredo123')
        cls.intruso = User.objects.create_user('intruso', password='segredo123')
        cls.cat = Categoria.objects.create(nome='Bikes', slug='bikes')
        cls.anuncio = Anuncio.objects.create(
            titulo='Bicicleta Caloi', descricao='aro 29', preco=Decimal('500'),
            cidade='Recife', categoria=cls.cat, vendedor=cls.dono,
        )

    def test_anonimo_e_mandado_pro_login(self):
        r = self.client.get(reverse('anuncios:editar', args=[self.anuncio.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/contas/login/', r['Location'])

    def test_intruso_nao_apaga(self):
        self.client.login(username='intruso', password='segredo123')
        self.client.post(reverse('anuncios:apagar', args=[self.anuncio.pk]))
        self.assertTrue(Anuncio.objects.filter(pk=self.anuncio.pk).exists())

    def test_intruso_nao_muda_a_situacao(self):
        self.client.login(username='intruso', password='segredo123')
        self.client.post(reverse('anuncios:mudar_situacao', args=[self.anuncio.pk]),
                         {'situacao': 'vendido'})
        self.anuncio.refresh_from_db()
        self.assertEqual(self.anuncio.situacao, 'disponivel')

    def test_dono_muda_a_situacao(self):
        self.client.login(username='dono', password='segredo123')
        self.client.post(reverse('anuncios:mudar_situacao', args=[self.anuncio.pk]),
                         {'situacao': 'vendido'})
        self.anuncio.refresh_from_db()
        self.assertEqual(self.anuncio.situacao, 'vendido')

    def test_situacao_invalida_e_recusada(self):
        self.client.login(username='dono', password='segredo123')
        self.client.post(reverse('anuncios:mudar_situacao', args=[self.anuncio.pk]),
                         {'situacao': 'hackeado'})
        self.anuncio.refresh_from_db()
        self.assertEqual(self.anuncio.situacao, 'disponivel')
