# Generated by Django 3.2.15 on 2022-08-27 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0053_alter_orderline_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, verbose_name='комментарий'),
        ),
    ]
