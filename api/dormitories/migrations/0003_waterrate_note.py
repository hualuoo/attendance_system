# Generated by Django 3.0.2 on 2020-03-03 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dormitories', '0002_waterrate_surplus_water'),
    ]

    operations = [
        migrations.AddField(
            model_name='waterrate',
            name='note',
            field=models.CharField(blank=True, max_length=100, verbose_name='备注'),
        ),
    ]