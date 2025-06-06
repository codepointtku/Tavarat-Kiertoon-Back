# Generated by Django 4.1.4 on 2023-04-17 04:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("products", "0001_initial"),
        ("bikes", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="bikerental",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="bikeamount",
            name="bike",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="bikes.bike"
            ),
        ),
        migrations.AddField(
            model_name="bikeamount",
            name="package",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bikes",
                to="bikes.bikepackage",
            ),
        ),
        migrations.AddField(
            model_name="bike",
            name="brand",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="bikes.bikebrand",
            ),
        ),
        migrations.AddField(
            model_name="bike",
            name="color",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="products.color",
            ),
        ),
        migrations.AddField(
            model_name="bike",
            name="size",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="bikes.bikesize",
            ),
        ),
        migrations.AddField(
            model_name="bike",
            name="type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="bikes.biketype",
            ),
        ),
    ]
