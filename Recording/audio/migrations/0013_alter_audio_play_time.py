# Generated by Django 3.2.5 on 2022-05-26 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0012_audio_wav_filepath'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audio',
            name='play_time',
            field=models.CharField(max_length=20, null=True),
        ),
    ]