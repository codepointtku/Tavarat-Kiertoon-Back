# Generated by Django 4.1.4 on 2023-05-02 04:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contact_forms", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contactform",
            name="status",
            field=models.CharField(
                choices=[
                    ("Not read", "Not Read"),
                    ("Read", "Read"),
                    ("Handled", "Handled"),
                ],
                default="Not read",
                max_length=255,
            ),
        ),
    ]
