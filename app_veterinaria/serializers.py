from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token
from .models import *
from datetime import datetime

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'

class TipoServicioSerializer(serializers.ModelSerializer):
    class Meta: 
        model = TipoServicio
        fields = '__all__'

class VeterinarioSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Veterinario
        fields = '__all__'

class ClientesSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Cliente
        fields = '__all__'

class RazaSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Raza
        fields = '__all__'

class TipoMascotaSerializer(serializers.ModelSerializer):
    class Meta: 
        model = TipoMascota
        fields = '__all__'

class MascotaSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Mascota
        fields = '__all__'

class CitasSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Cita
        fields = '__all__'


class PreguntaFrecuentesSerializer(serializers.ModelSerializer):
    class Meta: 
        model = PreguntaFrecuentes
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Usuario
        fields = '__all__'

#serializar el token para el inicio de session 
class AccesoTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token =  super(AccesoTokenSerializer , cls).get_token(user)

        token['usuario'] = user.username
        token['nombre_apellido'] = f"{user.first_name} {user.last_name}"
        token['correo'] = user.email
        token['documento'] = user.document_number
        token['key_rol'] = user.user_type.id
        token['rol'] = user.user_type.tipo_usuario
        token['permisos'] = MenuUsuario(user.user_type_id)
        
        Usuario.objects.filter(id = user.id).update(
            last_login = datetime.now()
        )
    
        return token

def MenuUsuario(keyTipoUsuario):
    permisos = AsignacionPermiso.objects.all().filter(key_tipo_usuario = keyTipoUsuario)

    datos = []
    for permiso in permisos:
        datos.append({
            'id' : permiso.id,
            "menu" : permiso.key_menu.menu,
            "permiso" : permiso.key_permiso.permiso
        })
    
    return datos



class AsignacionPermisoSerializer(serializers.ModelSerializer):
     class Meta: 
        model = AsignacionPermiso
        fields = '__all__'

class MedicamentoSerializer(serializers.ModelSerializer):
     class Meta: 
        model = Medicina
        fields = '__all__'
