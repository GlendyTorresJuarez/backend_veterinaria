# Generated by Django 4.0.3 on 2024-02-02 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_veterinaria', '0016_cita_key_servicio'),
    ]

    operations = [
        migrations.AddField(
            model_name='cita',
            name='motivo_cancelacion',
            field=models.TextField(blank=True, null=True),
        ),
    ]
