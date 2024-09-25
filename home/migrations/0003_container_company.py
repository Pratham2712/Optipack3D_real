# Generated by Django 5.1 on 2024-09-24 05:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_company_container_type_company_destination_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='container',
            name='company',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='containers', to='home.company'),
        ),
    ]