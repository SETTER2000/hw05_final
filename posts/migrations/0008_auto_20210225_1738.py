# Generated by Django 2.2.9 on 2021-02-25 14:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20210225_1255'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'get_latest_by': ['-priority', 'pub_date']},
        ),
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(verbose_name='group description'),
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(max_length=128, unique=True,
                                   verbose_name='url group'),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(max_length=200, verbose_name='post title'),
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL, verbose_name='author published'),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True,
                                    null=True,
                                    on_delete=django.db.models.deletion.
                                    CASCADE,
                                    to='posts.Group',
                                    verbose_name='list of groups'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(verbose_name='text published'),
        ),
        migrations.AlterModelTable(
            name='group',
            table='posts_group',
        ),
        migrations.AlterModelTable(
            name='post',
            table='posts_post',
        ),
    ]
