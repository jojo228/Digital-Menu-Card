# Generated by Django 3.1.7 on 2023-05-11 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QR', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='price',
            field=models.IntegerField(),
        ),
    ]
