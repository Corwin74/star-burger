# Generated by Django 3.2.15 on 2022-08-28 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geocode', '0002_alter_geocache_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geocache',
            name='lat',
            field=models.DecimalField(decimal_places=8, max_digits=10, null=True, verbose_name='широта'),
        ),
        migrations.AlterField(
            model_name='geocache',
            name='lon',
            field=models.DecimalField(decimal_places=8, max_digits=10, null=True, verbose_name='долгота'),
        ),
    ]
