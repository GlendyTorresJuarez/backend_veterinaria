# Generated by Django 4.0.3 on 2024-01-27 20:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dni', models.TextField(blank=True, null=True)),
                ('nombre', models.TextField(blank=True, null=True)),
                ('apellido', models.TextField(blank=True, null=True)),
                ('direccion', models.TextField(blank=True, null=True)),
                ('num_cel', models.IntegerField(blank=True, null=True)),
                ('correo', models.TextField(blank=True, null=True)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'cliente',
            },
        ),
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(blank=True, null=True)),
                ('abreviatura', models.TextField(blank=True, null=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('accion', models.TextField(blank=True, null=True)),
                ('color', models.TextField(blank=True, null=True)),
                ('icon', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'estado',
            },
        ),
        migrations.CreateModel(
            name='Evento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(blank=True, null=True)),
                ('color', models.TextField(blank=True, null=True)),
                ('icon', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'evento',
            },
        ),
        migrations.CreateModel(
            name='Raza',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_raza', models.TextField(blank=True, null=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'raza',
            },
        ),
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_servcio', models.TextField(blank=True, null=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('precio', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'servicio',
            },
        ),
        migrations.CreateModel(
            name='TipoEstado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(blank=True, null=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'tipo_estado',
            },
        ),
        migrations.CreateModel(
            name='TipoUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_usuario', models.TextField(blank=True, null=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'tipo_usuario',
            },
        ),
        migrations.CreateModel(
            name='Veterinario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(blank=True, null=True)),
                ('apellido', models.TextField(blank=True, null=True)),
                ('direccion', models.TextField(blank=True, null=True)),
                ('correo', models.TextField(blank=True, null=True)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('num_cel', models.TextField(blank=True, null=True)),
                ('key_estado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.estado')),
            ],
            options={
                'db_table': 'veterinario',
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(blank=True, null=True)),
                ('apellido', models.TextField(blank=True, null=True)),
                ('usuario', models.TextField(blank=True, null=True)),
                ('password', models.TextField(blank=True, null=True)),
                ('correo', models.TextField(blank=True, null=True)),
                ('token', models.TextField(blank=True, null=True)),
                ('token_recup', models.TextField(blank=True, null=True)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('key_tipo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.tipousuario')),
            ],
            options={
                'db_table': 'usuario',
            },
        ),
        migrations.CreateModel(
            name='ProgramacionCita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora', models.DateTimeField(blank=True, null=True)),
                ('asunto', models.TextField(blank=True, null=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('key_estado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.estado')),
                ('key_servicio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.servicio')),
                ('key_veterinario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.veterinario')),
            ],
            options={
                'db_table': 'programacion_cita',
            },
        ),
        migrations.CreateModel(
            name='Mascota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(blank=True, null=True)),
                ('fecha_nacimiento', models.TextField(blank=True, null=True)),
                ('sexo', models.TextField(blank=True, null=True)),
                ('color', models.TextField(blank=True, null=True)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('key_cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.cliente')),
                ('key_estado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.estado')),
                ('key_raza', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.raza')),
            ],
            options={
                'db_table': 'mascota',
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_tabla', models.TextField(blank=True, null=True)),
                ('key_tabla', models.IntegerField()),
                ('fecha_hora_registro', models.DateTimeField(auto_now_add=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('key_evento', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.evento')),
                ('key_usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.usuario')),
            ],
            options={
                'db_table': 'log',
            },
        ),
        migrations.AddField(
            model_name='estado',
            name='key_tipo_estado',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.tipoestado'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='key_estado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.estado'),
        ),
        migrations.CreateModel(
            name='Cita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('key_cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.cliente')),
                ('key_estado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.estado')),
                ('key_mascota', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.mascota')),
                ('key_veterinario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.veterinario')),
            ],
            options={
                'db_table': 'cita',
            },
        ),
    ]