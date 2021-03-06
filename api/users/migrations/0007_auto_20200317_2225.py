# Generated by Django 3.0.2 on 2020-03-17 22:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dormitories', '0008_auto_20200305_2205'),
        ('users', '0006_auto_20200317_1919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='lived_dormitory',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lives_users', to='dormitories.Dormitory', verbose_name='居住宿舍'),
        ),
    ]
