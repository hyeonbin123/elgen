# Generated by Django 3.2.5 on 2022-06-02 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0019_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='reply',
            name='split_filename',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
