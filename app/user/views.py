from django.shortcuts import render, redirect

from django.http import HttpResponse, HttpRequest
from django.views import generic
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _

from core.models import User


def logged_in_redirect():
    return redirect('https://gitlab.com')


def login_redirect(*args, **kwargs):
    return redirect(reverse_lazy('login'))


def logout_view(request: HttpRequest, *args, **kwargs):
    logout(request)
    return login_redirect()


class LoginView(generic.TemplateView):
    template_name = "login.html"

    extra_context = {
        'signup_url': reverse_lazy('signup')
    }

    def get(self, request: HttpRequest, *args, **kwargs):
        # Check for already logged-in user
        if request.user.is_authenticated:
            return logged_in_redirect()

        context = {
            **self.extra_context,
            'error': True if 'error' in request.GET else False,
        }

        return self.render_to_response(context)

    def post(self, request: HttpRequest, *args, **kwargs):
        """
        Create new user from given data
        """
        try:
            # Validate fields presence
            if 'username' not in request.POST or not request.POST['username']:
                raise ValidationError(_('o campo de usuário é obrigatório'))
            if 'password' not in request.POST or not request.POST['password']:
                raise ValidationError(_('o campo de senha é obrigatório'))

            # Search for target user
            user = authenticate(request, username=request.POST['username'],
                                password=request.POST['password'])

            # Check for authentication failure
            if user is None:
                raise ValidationError(_('credenciais inválidas'))

            # Persist user session
            login(request, user)

            return logged_in_redirect()
        except Exception as ex:
            print(repr(ex))
            # Something went wrong
            context = {
                **self.extra_context,
                'error': True
            }

            # Add error msg for validation errors
            if isinstance(ex, ValidationError):
                context['error_msg'] = ex.message

            return self.render_to_response(context, status=400)


class SignupView(generic.TemplateView):
    template_name = "signup.html"

    extra_context = {
        'login_url': reverse_lazy('login')
    }

    def get(self, request, *args, **kwargs):
        context = {
            **self.extra_context,
            'error': True if 'error' in request.GET else False,
        }
        return self.render_to_response(context)

    def post(self, request: HttpRequest, *args, **kwargs):
        """
        Create new user from given data
        """
        try:
            # Try creating new user
            fields = ['first_name', 'last_name', 'email', 'username',
                      'password']
            creation_payload = {field_name: request.POST[field_name] for field_name in
                                fields if field_name in request.POST}
            new_user: User = User.objects.create_user(**creation_payload)

            # Automatically logs-in user
            login(request, new_user)

            return logged_in_redirect()
        except Exception as ex:
            print(repr(ex))
            # Something went wrong
            context = {
                **self.extra_context,
                'error': True
            }

            # Check for validations
            if isinstance(ex, ValidationError):
                context['error_msg'] = ex.message

            # Check for duplicate username/email
            if isinstance(ex, IntegrityError):
                context['error_msg'] = _("essas informações já estão em uso")

            return self.render_to_response(context, status=400)
