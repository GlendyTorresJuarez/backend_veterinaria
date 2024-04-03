# Generated by Django 4.0.3 on 2024-02-10 23:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_veterinaria', '0018_preguntafrecuentes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('menu', models.TextField(blank=True, null=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'menu',
            },
        ),
        migrations.CreateModel(
            name='AsignacionPermiso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key_menu', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.menu')),
                ('key_usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.usuario')),
            ],
            options={
                'db_table': 'asignacion_permiso',
            },
        ),
    ]
