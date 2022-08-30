# Generated by Django 3.2.15 on 2022-08-21 17:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GeoCache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100, unique=True, verbose_name='адрес')),
                ('lat', models.DecimalField(decimal_places=8, max_digits=10, verbose_name='широта')),
                ('lon', models.DecimalField(decimal_places=8, max_digits=10, verbose_name='долгота')),
                ('timestamp', models.DateField(default=django.utils.timezone.now, verbose_name='обновлено')),
            ],
        ),
    ]