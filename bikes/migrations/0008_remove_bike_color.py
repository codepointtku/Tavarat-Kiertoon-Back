# Generated by Django 4.1.4 on 2023-11-06 12:48

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("bikes", "0007_alter_bikerental_state"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="bike",
            name="color",
        ),
    ]
