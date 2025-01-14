# Generated by Django 3.2.15 on 2022-08-13 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_order_orderline'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='first_name',
            new_name='firstname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='phone',
            new_name='phonenumber',
        ),
        migrations.RenameField(
            model_name='orderline',
            old_name='quntity',
            new_name='quantity',
        ),
        migrations.RemoveField(
            model_name='order',
            name='last_name',
        ),
        migrations.AddField(
            model_name='order',
            name='lastname',
            field=models.CharField(db_index=True, default='Иванов', max_length=50, verbose_name='фамилия'),
            preserve_default=False,
        ),
    ]
