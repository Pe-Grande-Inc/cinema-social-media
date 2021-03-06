import uuid

from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class Post(models.Model):
    MAX_POST_LENGTH = 4096

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_('Identificador único do Post'))
    author = models.ForeignKey('User', on_delete=models.CASCADE,
                               verbose_name=_('autor'), help_text=_('Autor do Post'),
                               related_name='posts', related_query_name='post')
    movie = models.ForeignKey('Title', on_delete=models.CASCADE,
                              verbose_name=_('filme'), help_text=_('Filme do Post'),
                              related_name='posts', related_query_name='post')
    content = models.TextField(null=False, editable=True, verbose_name=_('conteúdo'),
                               validators=[MaxLengthValidator(MAX_POST_LENGTH),
                                           MinLengthValidator(1)],
                               help_text=_('Conteúdo do post'))
    creation_date = models.DateTimeField(auto_now_add=True,
                                         verbose_name=_('data de criação'),
                                         help_text=_('Data de criação da postagem'))
    last_edited = models.DateTimeField(auto_now=True, verbose_name=_('data de edição'),
                                       help_text=_('data da última edição'))

    @property
    def like_count(self):
        return self.ratings.filter(positive=True).count()

    @property
    def dislike_count(self):
        return self.ratings.filter(positive=False).count()

    @property
    def comment_count(self):
        return self.comments.count()

    @property
    def post_details_url(self):
        return reverse_lazy('post-details', kwargs={'post_id': self.id})

    @property
    def post_comment_url(self):
        return reverse_lazy('post-comment', kwargs={'post_id': self.id})

    @property
    def post_like_url(self):
        return reverse_lazy('post-like', kwargs={'post_id': self.id})

    def __str__(self):
        return f'Post {self.id} from {self.author.id}'

    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')
