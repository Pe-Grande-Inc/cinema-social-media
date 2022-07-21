# Generated by Django 4.0.6 on 2022-07-21 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_title_popularity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='movie_id',
        ),
        migrations.AddField(
            model_name='post',
            name='movie',
            field=models.ForeignKey(default='4127956b-4aaf-4d40-9cf4-20f19a1704e2', help_text='Filme do Post', on_delete=django.db.models.deletion.CASCADE, related_name='posts', related_query_name='post', to='core.title', verbose_name='filme'),
            preserve_default=False,
        ),
    ]
