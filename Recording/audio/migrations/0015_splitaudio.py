# Generated by Django 3.2.5 on 2022-05-27 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0014_audio_is_split'),
    ]

    operations = [
        migrations.CreateModel(
            name='SplitAudio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wav_filepath', models.CharField(max_length=300)),
                ('split_filename', models.CharField(max_length=100)),
                ('split_filepath', models.CharField(max_length=300)),
            ],
            options={
                'db_table': 'split_audio',
            },
        ),
    ]
