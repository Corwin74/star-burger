# Generated by Django 3.2.15 on 2022-08-17 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_auto_20220817_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_type',
            field=models.CharField(choices=[('CASH', 'наличные'), ('CARD', 'электронно')], db_index=True, default='CASH', max_length=4, verbose_name='способ оплаты'),
        ),
    ]
