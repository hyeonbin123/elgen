# Generated by Django 3.2.5 on 2022-06-20 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_auto_20220620_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_name',
            field=models.CharField(max_length=10),
        ),
    ]
