# Generated by Django 5.1.1 on 2024-09-25 04:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_rename_created_when_passwordreset_created_time"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Restaurant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("place_id", models.CharField(max_length=255, null=True, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("vicinity", models.CharField(max_length=255, null=True)),
                (
                    "image",
                    models.ImageField(blank=True, null=True, upload_to="restaurants/"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FavoriteRestaurant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "restaurant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.restaurant",
                    ),
                ),
            ],
        ),
    ]