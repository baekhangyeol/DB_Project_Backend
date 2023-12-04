# Generated by Django 4.0.3 on 2023-12-04 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0021_alter_cartype_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartype',
            name='size',
            field=models.CharField(choices=[('small', '소형'), ('medium', '중형'), ('large', '대형')], max_length=6, verbose_name='차량 크기'),
        ),
    ]
