# Generated by Django 3.2.5 on 2022-05-03 11:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0003_auto_20220503_0944'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='audio',
            name='patient_age',
        ),
        migrations.RemoveField(
            model_name='audio',
            name='patient_gender',
        ),
    ]
