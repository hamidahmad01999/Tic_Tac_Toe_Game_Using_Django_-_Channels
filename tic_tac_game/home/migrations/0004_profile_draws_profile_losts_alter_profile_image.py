# Generated by Django 5.1.3 on 2024-11-30 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0003_profile"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="draws",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="profile",
            name="losts",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="profile",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to="profile/", verbose_name="user_image"
            ),
        ),
    ]