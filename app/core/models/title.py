import uuid
from typing import List
from urllib.parse import urljoin

from django.db import models
from django.utils.translation import gettext_lazy as _

from integrations.tmdb import TMDB


class TitleManager(models.Manager):
    def parse_tmdb_movie(self, movie):
        try:
            if 'media_type' not in movie or movie['media_type'] not in ('tv', 'movie'):
                return None

            if movie['vote_count'] < 10:
                return None

            if 'adult' in movie and movie['adult']:
                return None

            model_args = {
                "tmdb_id": movie['id'],
                "name": movie['title'],
                "overview": movie['overview'],
                "vote_average": movie['vote_average'],
                "external_url": f"https://www.themoviedb.org/{movie['media_type']}/{movie['id']}"
            }

            if 'backdrop_path' in movie and movie['backdrop_path']:
                model_args["backdrop_url"] = urljoin(
                    TMDB.configuration['base_backdrop_url'],
                    '.' + movie['backdrop_path'])

            if 'poster_path' in movie and movie['poster_path']:
                model_args["poster_url"] = urljoin(
                    TMDB.configuration['base_poster_url'],
                    '.' + movie['poster_path'])

            return self.model(**model_args)
        except Exception as ex:
            print(movie, repr(ex))
            return None

    def load_from_tmdb(self, movies: List):
        # Can be improved a lot
        parsed_titles = [self.parse_tmdb_movie(movie) for movie in movies]
        parsed_titles = [title for title in parsed_titles if title is not None]

        titles_by_tmdb_id = [title.tmdb_id for title in parsed_titles]
        results = Title.objects.filter(tmdb_id__in=titles_by_tmdb_id)
        results_by_tmdb_id = {title.tmdb_id: title for title in results}

        for title in parsed_titles:
            if title.tmdb_id in results_by_tmdb_id:
                db_title = results_by_tmdb_id[title.tmdb_id]
                db_title.name = title.name
                db_title.overview = title.overview
                db_title.vote_average = title.vote_average
                db_title.backdrop_url = title.backdrop_url
                db_title.poster_url = title.poster_url
                db_title.external_url = title.external_url
                db_title.save()
            else:
                title.save()

        return results


class Title(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_('Identificador interno do filme'))

    tmdb_id = models.BigIntegerField(verbose_name=_('TMDB ID'),
                                     help_text=_('Identificador do filme no TMBD'),
                                     unique=True,
                                     db_index=True)

    backdrop_url = models.URLField(verbose_name=_('URL do Banner'), null=True)
    poster_url = models.URLField(verbose_name=_('URL do Poster'), null=True)
    external_url = models.URLField(verbose_name=_('URL externa'), null=True)

    name = models.CharField(max_length=255, verbose_name=_('nome'),
                            help_text=_('Nome do filme/série'))
    overview = models.TextField()
    vote_average = models.FloatField(verbose_name=_('média dos votos'))

    creation_date = models.DateTimeField(auto_now_add=True,
                                         verbose_name=_('data de criação'),
                                         help_text=_('data de criação interna'))

    last_update = models.DateTimeField(auto_now=True,
                                       verbose_name=_('data de atualização'),
                                       help_text=_('data da última atualização'))

    objects = TitleManager()

    def __str__(self):
        return f'{self.id}/{self.tmdb_id} - {self.name}'
