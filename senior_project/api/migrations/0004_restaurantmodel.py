# Generated by Django 4.0.3 on 2022-03-21 19:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_rename_user_appuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='RestaurantModel',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('api.restaurant',),
        ),
    ]