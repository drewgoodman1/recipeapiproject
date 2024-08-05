# Generated by Django 4.2.14 on 2024-08-01 16:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipeapi', '0002_favoriterecipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='summary',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='favoriterecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='recipeapi.recipe'),
        ),
        migrations.AlterField(
            model_name='favoriterecipe',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL),
        ),
    ]
