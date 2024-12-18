# Generated by Django 3.2 on 2024-09-29 23:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0019_auto_20240929_1249"),
    ]

    operations = [
        migrations.AlterField(
            model_name="favoriterecipe",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorited_by",
                to="recipes.recipe",
            ),
        ),
    ]
