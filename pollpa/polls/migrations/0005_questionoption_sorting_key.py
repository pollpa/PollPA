# Generated by Django 2.1.7 on 2019-04-03 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0004_auto_20190403_0547'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionoption',
            name='sorting_key',
            field=models.FloatField(default=0),
        ),
    ]
