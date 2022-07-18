import uuid

from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Comment(models.Model):
    MAX_COMMENT_LENGTH = 2048

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_('Identificador único do comentário'))
    author = models.ForeignKey('User', on_delete=models.CASCADE,
                               verbose_name=_('autor'),
                               help_text=_('Autor do comentário'),
                               related_name='comments', related_query_name='comment')
    post = models.ForeignKey('Post', on_delete=models.CASCADE,
                             help_text=_('Post do comentário'), related_name='comments',
                             related_query_name='comment')
    content = models.TextField(null=False, editable=True, verbose_name=_('conteúdo'),
                               validators=[MaxLengthValidator(MAX_COMMENT_LENGTH),
                                           MinLengthValidator(1)],
                               help_text=_('Conteúdo do comentário'))
    creation_date = models.DateTimeField(auto_now_add=True,
                                         verbose_name=_('data de criação'),
                                         help_text=_('Data de criação do comentário'))
    last_edited = models.DateTimeField(auto_now=True, verbose_name=_('data de edição'),
                                       help_text=_('data da última edição'))

    @property
    def is_edited(self):
        return self.creation_date != self.last_edited

    def __str__(self):
        return f'Post {self.id} from {self.author.id}'
