# Generated by Django 3.2.3 on 2021-05-31 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('time_table', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='valid',
            field=models.IntegerField(default=1),
        ),
    ]
