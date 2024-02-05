# Generated by Django 3.2.5 on 2022-05-24 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0009_alter_audio_delete_reason'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('board_id', models.PositiveIntegerField()),
                ('user_id', models.CharField(max_length=50)),
                ('content', models.CharField(max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'db_table': 'reply',
            },
        ),
        migrations.CreateModel(
            name='ReReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reply_id', models.PositiveIntegerField()),
                ('user_id', models.CharField(max_length=50)),
                ('content', models.CharField(max_length=300)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'reReply',
            },
        ),
    ]