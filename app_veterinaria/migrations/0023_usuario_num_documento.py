# Generated by Django 4.0.3 on 2024-02-12 23:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_veterinaria', '0022_alter_usuario_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='num_documento',
            field=models.TextField(blank=True, null=True),
        ),
    ]
