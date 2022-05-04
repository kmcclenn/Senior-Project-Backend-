# Generated by Django 4.0.4 on 2022-05-04 01:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_inputtedwaittimes'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='user_who_created',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='restaurantscreated', to=settings.AUTH_USER_MODEL),
        ),
    ]
