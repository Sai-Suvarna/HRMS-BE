# Generated by Django 5.0.6 on 2024-12-06 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0002_alter_empworkdetails_userid'),
    ]

    operations = [
        migrations.AddField(
            model_name='empworkdetails',
            name='employmentType',
            field=models.CharField(default='Full Time', max_length=100),
        ),
    ]
