# Generated by Django 3.2.5 on 2023-01-18 05:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0046_delete_newpatient'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='audio',
            name='new_patient_id',
        ),
    ]