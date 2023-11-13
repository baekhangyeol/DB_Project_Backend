# Generated by Django 4.0.3 on 2023-11-13 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0015_alter_cartype_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartype',
            name='size',
            field=models.CharField(choices=[('medium', '중형'), ('large', '대형'), ('small', '소형')], max_length=6, verbose_name='차량 크기'),
        ),
    ]
