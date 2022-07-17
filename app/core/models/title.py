import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Title(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_('Identificador interno do filme'))

    tmdb_id = models.BigIntegerField(verbose_name=_('TMDB ID'),
                                     help_text=_('Identificador do filme no TMBD'),
                                     unique=True,
                                     db_index=True)

    backdrop_url = models.URLField(verbose_name=_('URL do Banner'))
    poster_url = models.URLField(verbose_name=_('URL do Poster'))
    name = models.CharField(max_length=255, verbose_name=_('nome'),
                            help_text=_('Nome do filme/série'))
    overview = models.TextField()
    vote_average = models.FloatField(verbose_name=_('média dos votos'))

    creation_date = models.DateTimeField(auto_now_add=True,
                                         verbose_name=_('data de criação'),
                                         help_text=_('data de criação interna'))

    last_update = models.DateTimeField(auto_now=True,
                                       verbose_name=_('data de atualização'),
                                       help_text=_('data da última atualização'))
