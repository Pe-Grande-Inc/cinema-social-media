import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class PostRating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_('Identificador único da avaliação'))
    post = models.ForeignKey('Post', on_delete=models.CASCADE,
                             help_text=_('Avaliação do Post'), related_name='ratings',
                             related_query_name='rating')
    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             verbose_name=_('usuário'),
                             help_text=_('Usuário que avaliou a postagem'),
                             related_name='ratings', related_query_name='rating')
    positive = models.BooleanField(verbose_name=_('positiva'),
                                   help_text=_(
                                       'Indica se a avaliação foi positiva ou negativa.'),
                                   editable=True)
    creation_date = models.DateTimeField(auto_now_add=True,
                                         verbose_name=_('data de criação'),
                                         help_text=_('Data de criação da avaliação'))

    class Meta:
        verbose_name = _('avaliação')
        verbose_name_plural = _('avaliações')
        unique_together = (('post', 'user'),)

    def __str__(self):
        return f'Rating of {self.post.id} from {self.user.username}: {"POSITIVE" if self.positive else "NEGATIVE"}'
