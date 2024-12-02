# Generated by Django 5.1.3 on 2024-11-29 06:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Game",
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
                ("room_code", models.CharField(max_length=100, unique=True)),
                ("game_creator", models.CharField(max_length=100)),
                (
                    "game_opponent",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("is_over", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Box",
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
                ("box_number", models.IntegerField()),
                (
                    "box_value",
                    models.CharField(blank=True, default="", max_length=1, null=True),
                ),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="boxes",
                        to="home.game",
                    ),
                ),
            ],
        ),
    ]
