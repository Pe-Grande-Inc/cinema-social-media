import uuid

from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Post(models.Model):
    MAX_POST_LENGTH = 4096

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_('Identificador único do Post'))
    author = models.ForeignKey('User', on_delete=models.CASCADE,
                               verbose_name=_('autor'), help_text=_('Autor do Post'),
                               related_name='posts', related_query_name='post')
    movie_id = models.IntegerField(null=False, editable=True,
                                   verbose_name=_('id do filme'), help_text=_(
            'ID do filme/série que o filme se trata'))
    content = models.TextField(null=False, editable=True, verbose_name=_('conteúdo'),
                               validators=[MaxLengthValidator(MAX_POST_LENGTH),
                                           MinLengthValidator(1)],
                               help_text=_('Conteúdo do post'))
    creation_date = models.DateTimeField(auto_now_add=True,
                                         verbose_name=_('data de criação'),
                                         help_text=_('Data de criação da postagem'))
    last_edited = models.DateTimeField(auto_now=True, verbose_name=_('data de edição'),
                                       help_text=_('data da última edição'))

    def __str__(self):
        return f'Post {self.id} from {self.author.id}'
