# Generated by Django 4.1.4 on 2023-07-13 06:00

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0014_remove_product_color_product_color"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="color",
            new_name="colors",
        ),
    ]
