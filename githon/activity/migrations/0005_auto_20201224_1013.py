# Generated by Django 3.1.2 on 2020-12-24 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0004_auto_20201224_1010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='id',
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
    ]
