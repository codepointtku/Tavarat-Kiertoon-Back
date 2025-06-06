# Generated by Django 4.1.4 on 2023-09-08 09:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0011_alter_order_status"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="contact",
            new_name="recipient",
        ),
        migrations.RenameField(
            model_name="order",
            old_name="phone_number",
            new_name="recipient_phone_number",
        ),
        migrations.AlterField(
            model_name="order",
            name="delivery_required",
            field=models.BooleanField(default=False),
        ),
    ]
