# Generated by Django 4.0.6 on 2022-07-22 17:11

from django.conf import settings
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Identificador único do Usuário', primary_key=True, serialize=False)),
                ('following', models.ManyToManyField(help_text='Usuários seguidos', related_name='followers', related_query_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='seguindo')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'usuário',
                'verbose_name_plural': 'usuários',
            },
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Identificador interno do filme', primary_key=True, serialize=False)),
                ('tmdb_id', models.BigIntegerField(db_index=True, help_text='Identificador do filme no TMBD', unique=True, verbose_name='TMDB ID')),
                ('backdrop_url', models.URLField(null=True, verbose_name='URL do Banner')),
                ('poster_url', models.URLField(null=True, verbose_name='URL do Poster')),
                ('external_url', models.URLField(null=True, verbose_name='URL externa')),
                ('name', models.CharField(help_text='Nome do filme/série', max_length=255, verbose_name='nome')),
                ('overview', models.TextField()),
                ('vote_average', models.FloatField(verbose_name='média dos votos')),
                ('popularity', models.FloatField(verbose_name='popularidade do título')),
                ('creation_date', models.DateTimeField(auto_now_add=True, help_text='data de criação interna', verbose_name='data de criação')),
                ('last_update', models.DateTimeField(auto_now=True, help_text='data da última atualização', verbose_name='data de atualização')),
            ],
            options={
                'verbose_name': 'título',
                'verbose_name_plural': 'títulos',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Identificador único do Post', primary_key=True, serialize=False)),
                ('content', models.TextField(help_text='Conteúdo do post', validators=[django.core.validators.MaxLengthValidator(4096), django.core.validators.MinLengthValidator(1)], verbose_name='conteúdo')),
                ('creation_date', models.DateTimeField(auto_now_add=True, help_text='Data de criação da postagem', verbose_name='data de criação')),
                ('last_edited', models.DateTimeField(auto_now=True, help_text='data da última edição', verbose_name='data de edição')),
                ('author', models.ForeignKey(help_text='Autor do Post', on_delete=django.db.models.deletion.CASCADE, related_name='posts', related_query_name='post', to=settings.AUTH_USER_MODEL, verbose_name='autor')),
                ('movie', models.ForeignKey(help_text='Filme do Post', on_delete=django.db.models.deletion.CASCADE, related_name='posts', related_query_name='post', to='core.title', verbose_name='filme')),
            ],
            options={
                'verbose_name': 'post',
                'verbose_name_plural': 'posts',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Identificador único do comentário', primary_key=True, serialize=False)),
                ('content', models.TextField(help_text='Conteúdo do comentário', validators=[django.core.validators.MaxLengthValidator(2048), django.core.validators.MinLengthValidator(1)], verbose_name='conteúdo')),
                ('creation_date', models.DateTimeField(auto_now_add=True, help_text='Data de criação do comentário', verbose_name='data de criação')),
                ('last_edited', models.DateTimeField(auto_now=True, help_text='data da última edição', verbose_name='data de edição')),
                ('author', models.ForeignKey(help_text='Autor do comentário', on_delete=django.db.models.deletion.CASCADE, related_name='comments', related_query_name='comment', to=settings.AUTH_USER_MODEL, verbose_name='autor')),
                ('post', models.ForeignKey(help_text='Post do comentário', on_delete=django.db.models.deletion.CASCADE, related_name='comments', related_query_name='comment', to='core.post')),
            ],
        ),
        migrations.CreateModel(
            name='PostRating',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Identificador único da avaliação', primary_key=True, serialize=False)),
                ('positive', models.BooleanField(help_text='Indica se a avaliação foi positiva ou negativa.', verbose_name='positiva')),
                ('creation_date', models.DateTimeField(auto_now_add=True, help_text='Data de criação da avaliação', verbose_name='data de criação')),
                ('post', models.ForeignKey(help_text='Avaliação do Post', on_delete=django.db.models.deletion.CASCADE, related_name='ratings', related_query_name='rating', to='core.post')),
                ('user', models.ForeignKey(help_text='Usuário que avaliou a postagem', on_delete=django.db.models.deletion.CASCADE, related_name='ratings', related_query_name='rating', to=settings.AUTH_USER_MODEL, verbose_name='usuário')),
            ],
            options={
                'verbose_name': 'avaliação',
                'verbose_name_plural': 'avaliações',
                'unique_together': {('post', 'user')},
            },
        ),
    ]
