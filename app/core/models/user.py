from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    validate_username = ASCIIUsernameValidator()

    def create_user(self, username: str = None, email: str = None, password: str = None, first_name: str = None, last_name: str = None, **extra_fields):
        if not username:
            raise ValidationError(_('Nome de usuário é obrigatório'))
        if not email:
            raise ValidationError(_('E-mail é obrigatório'))
        if not password:
            raise ValidationError(_('Senha é obrigatória'))
        if not first_name:
            raise ValidationError(_('Primeiro nome é obrigatório'))
        if not last_name:
            raise ValidationError(_('Sobrenome é obrigatório'))

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

    pass
