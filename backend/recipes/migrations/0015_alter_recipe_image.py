# Generated by Django 3.2.3 on 2024-09-26 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0014_rename_follow_subscription"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="image",
            field=models.ImageField(
                default=None, null=True, upload_to="users/avatars/"
            ),
        ),
    ]
