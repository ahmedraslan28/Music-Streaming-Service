# Generated by Django 4.2 on 2023-04-05 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_likedalbum_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptionplan',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
    ]