# Generated by Django 2.2.9 on 2021-02-25 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20210225_1738'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'get_latest_by': ['priority', 'pub_date']},
        ),
    ]