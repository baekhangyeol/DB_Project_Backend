# Generated by Django 4.2.7 on 2023-11-03 18:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0002_caroption_rename_bread_cartype_brand_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartype',
            name='size',
            field=models.CharField(choices=[('small', '소형'), ('large', '대형'), ('medium', '중형')], max_length=6, verbose_name='차량 크기'),
        ),
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('availability', models.BooleanField(default=True)),
                ('car_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='car.cartype')),
                ('options', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='car.caroption')),
            ],
            options={
                'verbose_name': '차량',
            },
        ),
    ]
