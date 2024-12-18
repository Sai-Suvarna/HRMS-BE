# Generated by Django 5.0.6 on 2024-12-05 06:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0001_initial'),
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PayCalculation',
            fields=[
                ('tsId', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('month', models.CharField(max_length=20)),
                ('no_of_days', models.IntegerField()),
                ('attendance', models.FloatField()),
                ('lop_days', models.FloatField()),
                ('OT', models.FloatField(default=0)),
                ('salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('basic', models.DecimalField(decimal_places=2, max_digits=10)),
                ('hra', models.DecimalField(decimal_places=2, max_digits=10)),
                ('da', models.DecimalField(decimal_places=2, max_digits=10)),
                ('special_allowance', models.DecimalField(decimal_places=2, max_digits=10)),
                ('grossPay', models.DecimalField(decimal_places=2, max_digits=10)),
                ('otPay', models.DecimalField(decimal_places=2, max_digits=10)),
                ('allowance', models.DecimalField(decimal_places=2, max_digits=10)),
                ('totalPay', models.DecimalField(decimal_places=2, max_digits=10)),
                ('eePF', models.DecimalField(decimal_places=2, max_digits=10)),
                ('esi', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pt', models.DecimalField(decimal_places=2, max_digits=10)),
                ('deductiblesLoans', models.DecimalField(decimal_places=2, max_digits=10)),
                ('deductions', models.DecimalField(decimal_places=2, max_digits=10)),
                ('net_pay', models.DecimalField(decimal_places=2, max_digits=10)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='company.companydetails')),
                ('empId', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employee.empworkdetails', to_field='empId')),
            ],
        ),
        migrations.CreateModel(
            name='TimeSheet',
            fields=[
                ('tsId', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('month', models.CharField(max_length=20)),
                ('no_of_days', models.IntegerField()),
                ('attendance', models.FloatField()),
                ('lop_days', models.FloatField()),
                ('OT', models.FloatField(default=0)),
                ('allowance', models.IntegerField(default=0)),
                ('deductions', models.IntegerField(default=0)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='company.companydetails')),
                ('empId', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employee.empworkdetails', to_field='empId')),
            ],
        ),
    ]
