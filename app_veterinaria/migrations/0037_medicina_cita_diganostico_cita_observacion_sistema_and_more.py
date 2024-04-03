# Generated by Django 4.0.3 on 2024-02-17 21:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_veterinaria', '0036_alter_permiso_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='Medicina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.TextField(blank=True, null=True)),
                ('nombre', models.TextField(blank=True, null=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('key_estado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.estado')),
            ],
            options={
                'db_table': 'medicina',
            },
        ),
        migrations.AddField(
            model_name='cita',
            name='diganostico',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cita',
            name='observacion_sistema',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cita',
            name='recomendacion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Triaje',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('peso', models.TextField(blank=True, null=True)),
                ('temperatura', models.TextField(blank=True, null=True)),
                ('frecuencia_cardica', models.TextField(blank=True, null=True)),
                ('frecuencia_respiratoria', models.TextField(blank=True, null=True)),
                ('key_cita', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.cita')),
            ],
            options={
                'db_table': 'triaje',
            },
        ),
        migrations.CreateModel(
            name='Receta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tratamiento', models.TextField(blank=True, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('key_cita', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.cita')),
                ('key_medicamento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.medicina')),
            ],
            options={
                'db_table': 'receta',
            },
        ),
    ]
