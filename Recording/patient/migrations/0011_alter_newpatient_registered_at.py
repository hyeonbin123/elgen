# Generated by Django 3.2.5 on 2023-01-19 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0010_alter_newpatient_old_patient_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newpatient',
            name='registered_at',
            field=models.DateField(),
        ),
    ]
