# Generated by Django 3.2.5 on 2023-01-30 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0016_alter_newpatient_delete_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newpatient',
            name='delete_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]