# Generated by Django 4.0.3 on 2024-05-18 23:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_veterinaria', '0040_rename_diganostico_cita_diagnostico'),
    ]

    operations = [
        migrations.CreateModel(
            name='RestablerUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('toke', models.TextField(blank=True, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('expired', models.DateTimeField()),
                ('codigo_recuperacion', models.TextField()),
                ('is_activo', models.BooleanField(default=True)),
                ('key_usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'restablecer_usuario',
            },
        ),
    ]
