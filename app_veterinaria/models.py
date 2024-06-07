from django.db import models
from django.contrib.auth.models import AbstractUser , Group, Permission
from django.utils import timezone

# Create your models here.
class TipoEstado(models.Model):
    nombre = models.TextField(null= True , blank= True)
    descripcion = models.TextField(null= True , blank= True)

    class Meta:
        db_table = 'tipo_estado'

class Estado(models.Model):
    nombre = models.TextField(null= True , blank= True)
    abreviatura = models.TextField(null= True , blank= True)
    descripcion = models.TextField(null= True , blank= True)
    accion = models.TextField(null= True , blank= True)
    color = models.TextField(null= True , blank= True)
    icon = models.TextField(null= True , blank= True)
    key_tipo_estado = models.ForeignKey(TipoEstado , blank=True ,on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'estado'

class Cliente(models.Model):
    key_estado = models.ForeignKey(Estado , null = True ,blank = True ,on_delete=models.CASCADE)
    dni = models.TextField(null = True, blank = True)
    nombre = models.TextField(null = True, blank = True)
    apellido = models.TextField(null = True, blank = True)
    direccion = models.TextField(null = True, blank = True)
    num_cel = models.TextField(null = True, blank = True)
    correo = models.TextField(null = True, blank = True)
    sexo = models.TextField(blank = True , null = True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cliente'

class TipoMascota(models.Model):
    tipo = models.TextField(blank=True, null=True)
    descripcion = models.TextField(null= True , blank= True)
    key_estado = models.ForeignKey(Estado , null = True ,blank = True ,on_delete=models.CASCADE)

    class Meta:
        db_table = 'tipo_mascota'

class Raza(models.Model):
    nombre_raza = models.TextField(null = True, blank = True)
    descripcion = models.TextField(null = True, blank = True)
    key_estado = models.ForeignKey(Estado , null = True ,blank = True ,on_delete=models.CASCADE)

    class Meta:
        db_table = 'raza'

class Mascota(models.Model):
    key_cliente = models.ForeignKey(Cliente , null=True , blank= True, on_delete = models.CASCADE)
    key_raza = models.ForeignKey(Raza , null=True , blank= True, on_delete = models.CASCADE)
    key_estado = models.ForeignKey(Estado , null=True, blank= True, on_delete = models.CASCADE)
    nombre = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.TextField(blank=True, null=True)
    sexo = models.TextField(blank=True, null=True)
    color = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    key_tipo_mascota = models.ForeignKey(TipoMascota , null = True ,blank = True ,on_delete=models.CASCADE)

    class Meta:
        db_table = 'mascota'

class TipoServicio(models.Model):
    tipo_servicio = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    key_estado = models.ForeignKey(Estado , blank = True , null = True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'tipo_servicio'

class Servicio(models.Model):
    nombre_servicio = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.FloatField(blank=True, null=True)
    duracion = models.TextField(blank = True , null = True)
    key_estado = models.ForeignKey(Estado , blank = True , null = True, on_delete=models.CASCADE)
    key_tipo_servicio = models.ForeignKey(TipoServicio , blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'servicio'

class Veterinario(models.Model):
    dni = models.TextField(null = True, blank = True)
    nombre = models.TextField(blank=True, null=True)
    apellido = models.TextField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    num_cel = models.TextField(blank = True , null = True)
    sexo = models.TextField(blank = True , null = True)
    correo = models.TextField(blank = True, null = True)
    key_estado = models.ForeignKey(Estado , blank = True , null = True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'veterinario'

class TipoCita(models.Model):
    tipo_cita = models.TextField(blank = True, null = True)
    descripcion = models.TextField(blank = True, null = True)
    key_estado = models.ForeignKey(Estado , blank = True , null = True, on_delete = models.CASCADE)

    class Meta:
        db_table = 'tipo_cita'

class Cita(models.Model):
    key_servicio = models.ForeignKey(Servicio , blank = True , null = True, on_delete=models.CASCADE)
    key_tipo_cita = models.ForeignKey(TipoCita , blank = True, null=True , on_delete=models.CASCADE)
    key_veterinario = models.ForeignKey(Veterinario , blank = True , null = True, on_delete = models.CASCADE)
    key_cliente = models.ForeignKey(Cliente , blank = True , null = True, on_delete = models.CASCADE)
    key_mascota = models.ForeignKey(Mascota , blank = True , null = True, on_delete = models.CASCADE)
    key_estado = models.ForeignKey(Estado , blank = True , null = True, on_delete = models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateField(blank = True , null = True)
    hora_inicio = models.TextField(blank = True , null = True)
    hora_fin = models.TextField(blank = True , null = True)
    motivo_consulta = models.TextField(blank = True , null = True)
    motivo_cancelacion = models.TextField(blank = True , null = True)
    observacion_sistema = models.TextField(blank = True , null = True)
    diagnostico = models.TextField(blank = True , null = True)
    recomendacion = models.TextField(blank = True , null = True)
    tiempo_estimado = models.TextField(blank = True , null = True)

    class Meta:
        db_table = 'cita'

class Triaje(models.Model):
    key_cita = models.ForeignKey(Cita , blank = True , null = True , on_delete = models.CASCADE)
    peso = models.TextField(blank = True , null = True)
    temperatura = models.TextField(blank = True , null = True)
    frecuencia_cardica = models.TextField(blank = True , null = True)
    frecuencia_respiratoria = models.TextField(blank = True , null = True)

    class Meta:
        db_table = 'triaje'

class Medicina(models.Model):
    codigo = models.TextField(blank = True , null = True)
    nombre = models.TextField(blank = True , null = True)
    descripcion = models.TextField(blank = True , null = True)
    key_estado = models.ForeignKey(Estado , blank = True , null = True , on_delete = models.CASCADE)
   

    class Meta:
        db_table = 'medicina'

class Receta(models.Model):
    key_cita = models.ForeignKey(Cita , blank = True , null = True , on_delete = models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'receta'

class Detalle_receta(models.Model):
    key_receta = models.ForeignKey(Receta , blank = True , null = True , on_delete = models.CASCADE)
    key_medicamento = models.ForeignKey(Medicina , blank = True , null = True , on_delete = models.CASCADE)
    tratamiento = models.TextField(blank = True , null = True)

    class Meta:
        db_table = 'detalle_receta'

class TipoUsuario(models.Model):
    tipo_usuario = models.TextField(blank = True, null = True)
    action = models.TextField(blank = True, null = True)
    descripcion = models.TextField(blank = True, null = True)

    class Meta:
        db_table = 'tipo_usuario'
  

class Menu(models.Model):
    menu = models.TextField(blank = True, null = True)
    descripcion = models.TextField(blank = True, null = True)

    class Meta:
        db_table = 'menu'

class Permiso(models.Model):
    permiso = models.TextField(blank = True, null = True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    key_estado = models.ForeignKey(Estado , blank = True , null = True, on_delete = models.CASCADE)

    class Meta:
        db_table = 'permiso'

class AsignacionPermiso(models.Model):
    key_menu = models.ForeignKey(Menu , null=True, blank=True, on_delete=models.CASCADE)
    key_tipo_usuario = models.ForeignKey(TipoUsuario , null=True, blank=True, on_delete=models.CASCADE)
    key_permiso = models.ForeignKey(Permiso , null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'asignacion_permiso'

class Usuario(AbstractUser): 
    document_number = models.TextField(unique=True)
    last_login = models.DateTimeField(default=timezone.now)
    user_type = models.ForeignKey(TipoUsuario , blank=True , null=True, on_delete= models.CASCADE)
    status = models.ForeignKey(Estado , blank=True , null=True, on_delete= models.CASCADE)

    # Agregar related_name para evitar conflictos
    groups = models.ManyToManyField(Group, related_name='usuarios', blank=True )
    user_permissions = models.ManyToManyField(Permission, related_name='usuarios_permissions' ,blank=True)

    
    class Meta:
        db_table = "usuario"
    
    #AGREGAR MIS CAMPOS AL MODELO SUPER USUARIO
    REQUIRED_FIELDS = ['document_number', 'user_type' , 'status']

class RestablerUsuario(models.Model):
    key_usuario = models.ForeignKey(Usuario , null=True, blank=True  , on_delete=models.CASCADE)
    toke = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    expired  = models.DateTimeField(null=False, blank=False)
    codigo_recuperacion = models.TextField(null=False, blank=False)
    is_activo = models.BooleanField(default=True)

    class Meta:
        db_table = "restablecer_usuario"

class Evento(models.Model):
    nombre = models.TextField(null=True, blank=True)
    color = models.TextField(null=True, blank=True)
    icon = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'evento'

class Log(models.Model):
    key_evento = models.ForeignKey(Evento , blank=True ,on_delete=models.CASCADE) 
    nombre_tabla = models.TextField(null=True, blank=True)
    key_tabla = models.IntegerField()
    fecha_hora_registro = models.DateTimeField(auto_now_add=True)
    key_usuario = models.ForeignKey(Usuario ,null=True, blank=True, on_delete=models.CASCADE)
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'log'

class PreguntaFrecuentes(models.Model):
    key_estado = models.ForeignKey(Estado , blank = True , null = True, on_delete=models.CASCADE)
    asunto = models.TextField(null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'pregunta_frecuente'











