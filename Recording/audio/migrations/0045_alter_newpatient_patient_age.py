# Generated by Django 3.2.5 on 2023-01-11 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0044_newpatient_old_patient_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newpatient',
            name='patient_age',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
