# Generated by Django 3.2.5 on 2022-05-11 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0005_patient'),
    ]

    operations = [
        migrations.AddField(
            model_name='audio',
            name='is_local_upload',
            field=models.CharField(default='N', max_length=10),
        ),
    ]