# Generated by Django 3.2.5 on 2022-05-03 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0002_audio_delete_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='audio',
            name='number_of_people',
            field=models.CharField(default=None, max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='audio',
            name='patient_id',
            field=models.CharField(default=None, max_length=10),
            preserve_default=False,
        ),
    ]