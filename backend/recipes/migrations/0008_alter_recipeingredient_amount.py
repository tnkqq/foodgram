# Generated by Django 3.2.3 on 2024-09-24 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0007_rename_image_user_avatar"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipeingredient",
            name="amount",
            field=models.PositiveIntegerField(),
        ),
    ]
