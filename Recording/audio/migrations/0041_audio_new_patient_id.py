# Generated by Django 3.2.5 on 2023-01-06 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0040_auto_20230106_1630'),
    ]

    operations = [
        migrations.AddField(
            model_name='audio',
            name='new_patient_id',
            field=models.CharField(default='00000', max_length=10),
        ),
    ]