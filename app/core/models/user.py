from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    following = models.ManyToManyField('self', symmetrical=False,
                                       verbose_name=_('seguindo'),
                                       help_text=_('Usuários seguidos'),
                                       related_name='followers',
                                       related_query_name='follower')

    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')

    pass
