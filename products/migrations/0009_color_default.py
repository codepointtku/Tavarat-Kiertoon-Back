# Generated by Django 4.1.4 on 2023-05-16 07:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0008_alter_product_barcode_alter_product_category_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="color",
            name="default",
            field=models.BooleanField(default=False),
        ),
    ]
