# Generated by Django 3.2.5 on 2023-01-11 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0043_auto_20230109_1353'),
    ]

    operations = [
        migrations.AddField(
            model_name='newpatient',
            name='old_patient_id',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
