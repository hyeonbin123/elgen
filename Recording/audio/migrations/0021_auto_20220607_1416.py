# Generated by Django 3.2.5 on 2022-06-07 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0020_reply_split_filename'),
    ]

    operations = [
        migrations.AddField(
            model_name='audio',
            name='is_requested',
            field=models.CharField(default='N', max_length=10),
        ),
        migrations.AddField(
            model_name='text',
            name='is_requested',
            field=models.CharField(default='N', max_length=10),
        ),
    ]
