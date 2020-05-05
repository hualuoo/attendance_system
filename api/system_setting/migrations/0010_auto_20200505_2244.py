# Generated by Django 3.0.2 on 2020-05-05 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system_setting', '0009_systemlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemsetting',
            name='note',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='备注'),
        ),
        migrations.AlterField(
            model_name='systemsetting',
            name='url',
            field=models.FileField(blank=True, null=True, upload_to='media/file/', verbose_name='链接'),
        ),
    ]
