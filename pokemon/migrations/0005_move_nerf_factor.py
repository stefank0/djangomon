# Generated by Django 3.2.4 on 2021-06-26 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokemon', '0004_auto_20201107_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='move',
            name='nerf_factor',
            field=models.FloatField(default=1.0),
        ),
    ]
