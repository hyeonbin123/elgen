# Generated by Django 3.2.5 on 2022-05-31 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='order',
            field=models.PositiveIntegerField(null=True, unique=True),
        ),
    ]
