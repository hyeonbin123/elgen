# Generated by Django 3.2.5 on 2022-05-30 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0017_auto_20220530_1025'),
    ]

    operations = [
        migrations.AddField(
            model_name='audio',
            name='status',
            field=models.CharField(max_length=20, null=True),
        ),
    ]