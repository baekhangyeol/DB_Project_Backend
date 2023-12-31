# Generated by Django 4.2.7 on 2023-11-03 19:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0001_initial'),
        ('car', '0005_carmaintenance'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='branch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cars', to='employee.branch'),
        ),
        migrations.AlterField(
            model_name='cartype',
            name='size',
            field=models.CharField(choices=[('medium', '중형'), ('small', '소형'), ('large', '대형')], max_length=6, verbose_name='차량 크기'),
        ),
    ]
