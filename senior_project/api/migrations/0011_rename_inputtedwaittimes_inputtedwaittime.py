# Generated by Django 4.0.4 on 2022-05-04 17:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_remove_appuser_credibility_rating_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='InputtedWaittimes',
            new_name='InputtedWaittime',
        ),
    ]
