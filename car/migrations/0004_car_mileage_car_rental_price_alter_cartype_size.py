# Generated by Django 4.2.7 on 2023-11-03 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0003_alter_cartype_size_car'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='mileage',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='car',
            name='rental_price',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='cartype',
            name='size',
            field=models.CharField(choices=[('large', '대형'), ('small', '소형'), ('medium', '중형')], max_length=6, verbose_name='차량 크기'),
        ),
    ]
