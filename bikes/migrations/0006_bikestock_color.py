# Generated by Django 4.1.4 on 2023-07-10 07:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0014_remove_product_color_product_color"),
        ("bikes", "0005_alter_bikestock_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="bikestock",
            name="color",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="products.color",
            ),
        ),
    ]
