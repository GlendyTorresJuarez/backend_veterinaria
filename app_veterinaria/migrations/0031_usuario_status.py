# Generated by Django 4.0.3 on 2024-02-13 23:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_veterinaria', '0030_rename_num_documento_usuario_document_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_veterinaria.estado'),
        ),
    ]
