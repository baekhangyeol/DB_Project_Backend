# Generated by Django 4.2.7 on 2023-11-04 06:54

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('car', '0008_alter_cartype_size'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('driver_license_number', models.CharField(max_length=50)),
                ('join_date', models.DateField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': '고객',
            },
        ),
        migrations.CreateModel(
            name='Rental',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('total_amount', models.IntegerField()),
                ('payment_method', models.CharField(max_length=50)),
                ('status', models.CharField(choices=[('reserved', '예약'), ('in_progress', '진행 중'), ('completed', '종료')], default='reserved', max_length=20)),
                ('car', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rentals', to='car.car')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rentals', to='customer.customer')),
            ],
            options={
                'verbose_name': '대여',
            },
        ),
    ]
