# Generated by Django 3.2.15 on 2022-08-15 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_auto_20220815_0631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderline',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Цена'),
        ),
    ]