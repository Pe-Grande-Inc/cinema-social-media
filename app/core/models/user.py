import uuid
from hashlib import md5

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    validate_username = ASCIIUsernameValidator()

    def create_user(self, username: str = None, email: str = None, password: str = None,
                    first_name: str = None, last_name: str = None, **extra_fields):
        if not first_name:
            raise ValidationError(_('primeiro nome é obrigatório'))
        if not last_name:
            raise ValidationError(_('sobrenome é obrigatório'))
        if not username:
            raise ValidationError(_('nome de usuário é obrigatório'))
        if not email:
            raise ValidationError(_('e-mail é obrigatório'))
        if not password:
            raise ValidationError(_('senha é obrigatória'))

        validate_password(password)
        self.validate_username(username)

        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_super_user(self, **fields):
        payload = {
            **fields,
            'is_staff': True,
            'is_superuser': True
        }

        return self.create_user(**payload)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_('Identificador único do Usuário'))

    following = models.ManyToManyField('self', symmetrical=False,
                                       verbose_name=_('seguindo'),
                                       help_text=_('Usuários seguidos'),
                                       related_name='followers',
                                       related_query_name='follower')

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')

    @property
    def avatar_url(self):
        email_hash = md5(self.email.strip().lower().encode("utf-8"))
        email_hash_hex = email_hash.hexdigest()
        return f"https://www.gravatar.com/avatar/{email_hash_hex}?d=identicon"

    @property
    def follow_url(self):
        return reverse_lazy('follow-user', kwargs={'user_id': str(self.id)})

    @property
    def follow_url_search(self):
        return reverse_lazy('follow') + f"?user_id={self.id}"

    @property
    def feed_url(self):
        return reverse_lazy('feed') + f"?author={self.id}"
