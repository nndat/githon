# Generated by Django 3.1.2 on 2020-11-15 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='start_date',
            field=models.DateField(),
        ),
    ]
