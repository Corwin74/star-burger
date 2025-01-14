# Generated by Django 3.2.15 on 2022-08-15 07:31

from django.db import migrations


def fixprice(apps, schema_editor):
    Product = apps.get_model('foodcartapp', 'Product')
    products = Product.objects.all().iterator()
    for product in products:
        product.lines.all().update(price=product.price)


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_alter_orderline_price'),
    ]

    operations = [
        migrations.RunPython(fixprice),
    ]
