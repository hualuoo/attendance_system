# Generated by Django 3.0.2 on 2020-03-02 15:21

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dormitory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=10, verbose_name='编号')),
                ('area', models.CharField(max_length=3, verbose_name='宿舍区域')),
                ('build', models.CharField(max_length=1, verbose_name='宿舍楼')),
                ('floor', models.IntegerField(verbose_name='宿舍楼层')),
                ('room', models.CharField(max_length=4, verbose_name='房间号')),
                ('allow_live_number', models.IntegerField(verbose_name='允许居住人数')),
                ('now_live_number', models.IntegerField(default=0, verbose_name='现已居住人数')),
                ('note', models.CharField(blank=True, max_length=100, verbose_name='备注')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '宿舍房间',
                'verbose_name_plural': '宿舍房间',
            },
        ),
        migrations.CreateModel(
            name='WaterRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('used_water', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='已用水量(吨)')),
                ('total_water', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='总共水量(吨)')),
                ('month', models.DateField(verbose_name='月份')),
                ('dormitory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='water_rate_dormitory', to='dormitories.Dormitory', verbose_name='宿舍')),
            ],
            options={
                'verbose_name': '宿舍水费',
                'verbose_name_plural': '宿舍水费',
            },
        ),
    ]
