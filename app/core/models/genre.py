import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_('Identificador interno do gênero'))

    tmdb_id = models.BigIntegerField(verbose_name=_('TMDB ID'),
                                     help_text=_('Identificador do gênero no TMBD'),
                                     unique=True,
                                     db_index=True)

    tv = models.BooleanField(default=False, help_text=_(
        'Identifica se é um gênero de filme ou de série'))
