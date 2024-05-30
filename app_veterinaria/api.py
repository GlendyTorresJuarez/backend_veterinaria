
from .models  import *
import io
import pandas as pd
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from rest_framework.decorators import api_view
from .serializers import *
from django.db import connections
import requests
from django.db.models import Q
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.views import TokenObtainPairView

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm, mm
from io import BytesIO
from django.conf import settings
import os
from django.template.defaultfilters import date
from reportlab.lib.pagesizes import letter
from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings
from django.template.loader import render_to_string
import secrets
import string
import random


@api_view(['POST'])
def ListaHistorial(request):
    try:
        if request.method == 'POST':
            keyTabla = request.data['key_tabla']
            nombreTabla = request.data['nombre_tabla']

            consulta = ConsultarLog(keyTabla , nombreTabla)
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 


def RegistrarHistorial(keyEvento , nombreTabla , keyTabla , keyUsuario , descripcion):
    log = Log.objects.create(
        key_evento_id = keyEvento,
        nombre_tabla = nombreTabla,
        key_tabla = keyTabla,
        key_usuario_id = keyUsuario,
        descripcion =  descripcion
    )

    return log.id

def ConvertirQueryADiccionarioDato(cursor):
    columna = [desc[0] for desc in cursor.description]
    return [dict(zip(columna, fila)) for fila in cursor.fetchall()]

#---------------------API CONSULTA DE RENIEC---------------------
@api_view(['GET'])
def ApiReniec(request , dni):
    try:
        url = f"https://api.apis.net.pe/v1/dni?numero={dni}"
        response = requests.request("GET" , url , headers= {} , data={})

        if response.status_code == 200:
            isError = False
            message = "Operación con exito"
            data = response.json()
        else:
            isError = True
            message = "Operación sin exito"
            data = []

        return Response({"is_error": isError, "message" : message , "data" : data} , status = status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 


@api_view(['GET'])
def ListaServicios(request):
    try:
        if request.method == 'GET':
            consulta = ConsultarServicios()
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 
    

def ConsultarServicios():
    try:
        query = """
        SELECT 
        ser.id,
        ser.nombre_servicio, 
        ser.descripcion,
        ser.precio,
        ser.duracion,
        ser.key_estado_id as key_estado,
        es.nombre,
        es.color,
        es.icon,
        tp.id as key_tipo_servicios,
        tp.tipo_servicio
        FROM servicio ser
        LEFT JOIN estado es on es.id = ser.key_estado_id
        LEFT JOIN tipo_servicio tp on tp.id = ser.key_tipo_servicio_id
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}
    

def ConsultarLog(keyTabla , nombreTabla ):
    try:
        query = f"""
        SELECT 
        l.id,
        l.nombre_tabla,
        l.fecha_hora_registro,
        l.descripcion,
        ev.nombre,
        ev.color,
        ev.icon,
        us.username as nombre_usuario
        FROM log l
        LEFT JOIN evento ev on ev.id = l.key_evento_id
        LEFT JOIN usuario us on us.id = l.key_usuario_id
        WHERE l.nombre_tabla = '{nombreTabla}' and l.key_tabla = {keyTabla}
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}

@api_view(['POST'])
def AgregarServicios(request):
    try: 
        if request.method == 'POST':
            print(request.data)
            isServicios = Servicio.objects.filter(nombre_servicio = request.data['nombre_servicio'])

            if isServicios.count() == 0:
                servicioSerializer = ServicioSerializer(data = request.data)

                if servicioSerializer.is_valid():
                    servicioSerializer.save()

                    keyServicio = servicioSerializer.data['id']
                    isError = False
                    message = "Informacion guarda con exito"

                    descripcion = f"El servicio por nombre {request.data['nombre_servicio']} fue registrado con exito"

                    RegistrarHistorial(1 , "servicio",keyServicio, request.data['key_usuario'], descripcion)
            else: 
                isError = True
                message = "La informacion ya se encuentra registrada en nuestra base de datos"
            
            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)

    except Exception as error:	
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

@api_view(['PUT'])
def ActualizarServicio(request , pk=None):
    try: 
        if request.method == 'PUT':
            isServicio = Servicio.objects.filter(id = pk).first()

            if isServicio:
                servicioSerializer = ServicioSerializer(isServicio , data = request.data)

                if servicioSerializer.is_valid():
                    servicioSerializer.save()
                    isError = False
                    message = "El servicio fue actualizado con exito"

                    descripcion = f"El servicio por nombre {request.data['nombre_servicio']} fue modificado con exito"
                
                    RegistrarHistorial(2 , "servicio", pk, request.data['key_usuario'], descripcion)
                else:
                    isError = True
                    message = f"error de lectura por lo siguiente: {servicioSerializer.errors}"
            else:
                isError = True
                message = "El servicio no se encuentra registrado en nuestra base de datos"
            
            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK) 

    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

@api_view(['PUT' , 'DELETE']) 
def EliminacionFiscaLogica(request , pk = None):
    try:
        isServicio = Servicio.objects.filter(id = pk)
        keyEvento = 0
        keyUsuario = request.data['key_usuario']

        if isServicio.first():
            if request.method == 'PUT':
                keyEstado = request.data['key_estado']

                isServicio.update(key_estado_id = keyEstado)
                isError = False
                message = "El servicio fue restaurado con exito" if keyEstado == 1 else "El servicio fue anulado con exito"
                keyEvento = 6 if keyEstado == 1 else 3

            elif request.method == 'DELETE':
                isServicio.delete()
                keyEvento = 4
                isError = False
                message = "El servicio fue eliminado con exito"
            
            RegistrarHistorial(keyEvento, 'servicio', pk , keyUsuario , message)
        else: 
            isError = True
            message = "El Servicio que desea actualizar o eliminar no se encuentra en nuestra base de datos"

        return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 


@api_view(['POST'])
def ExportarServicios(request):
    try:
        listaServicio = ConsultarServicios()
        
        if listaServicio['is_error'] == False and len(listaServicio['data']) != 0:
            df = pd.DataFrame(listaServicio['data'])
            df = df.drop(columns = ['id' , 'key_estado', 'nombre', 'color' , 'icon' , 'key_tipo_servicios'])
            df.columns = ['SERVICIOS' , 'DESCRIPCIÓN' , 'PRECIOS' ,'DURACION' , "TIPO SERVICIOS"]
        else: 
            columnsServicios = [{'SERVICIOS' : '' , 'DESCRIPCIÓN': '', 'PRECIOS' : '' , 'DURACION' : '' , "TIPO SERVICIOS" : ''}]
            df = pd.DataFrame(columnsServicios)

        crearExcel = CreateExcel(df , 'A1:C1', 'servicios')

        if crearExcel['status'] == False:
            contexto = crearExcel['result']
            return contexto
    except Exception as error:
        print(error)
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 
    
##--------------------CREACIÓN DEL ARCHIVO EXCEL ---------------------
def CreateExcel(df , filter , nombreArchivo):
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output , engine="xlsxwriter") as writer:
            df.to_excel(writer , sheet_name = nombreArchivo, index = False)
            workbook = writer.book
            worksheet = writer.sheets[nombreArchivo]

            formatHead = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter',
                                             'fg_color': '#28B463', 'font_color': '#FBFCFC', 'border': 1, 'font_size': '10'})
            worksheet.write_row(0, 0, df.columns, formatHead)
            worksheet.freeze_panes(1, 0)
            worksheet.autofilter(filter)

            for i, col in enumerate(df.columns):
                columnLen = max(df[col].astype(str).str.len().max() + 5 , len(col) + 5)
                worksheet.set_column(i, i , columnLen)
        response = HttpResponse(content = output.getvalue() , content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        status = False
        message = "Se creo correctamente el excel."
    
        return {"message" : message , "result" : response , "status" : status}
    
    except Exception as error:
        status = True
        message = str(error)
    
        return {"message" : message , "result" : [] , "status": status}

##--------------------CRUD DE TIPO DE SERVICIO ---------------------
@api_view(['GET'])
def ListarTipoServicios(request):
    try:
        if request.method == 'GET':
            consulta = ConsultaTipoServicio()
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return {'is_error': True , "message": str(error)}

def ConsultaTipoServicio():
    try:
        query = f"""
        select 
        tp.id,
        tp.tipo_servicio,
        tp.descripcion,
        es.id as key_estado,
        es.nombre as estado,
        es.color
        from tipo_servicio tp
        LEFT JOIN estado es on es.id = tp.key_estado_id	
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}

@api_view(['POST'])
def AgregarTipoServicios(request):
    try: 
        if request.method == 'POST':
            isServicios = TipoServicio.objects.filter(tipo_servicio = request.data['tipo_servicio'])

            if isServicios.count() == 0:
                tipoServicioSerializer = TipoServicioSerializer(data = request.data)

                if tipoServicioSerializer.is_valid():
                    tipoServicioSerializer.save()

                    keyTipoServicio = tipoServicioSerializer.data['id']
                    isError = False
                    message = "Informacion guarda con exito"

                    descripcion = f"El tipo de servicio por nombre {request.data['tipo_servicio']} fue registrado con exito"

                    RegistrarHistorial(1 , "tipo_servicio",keyTipoServicio, request.data['key_usuario'], descripcion)
            else: 
                isError = True
                message = "La informacion ya se encuentra registrada en nuestra base de datos"
            
            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)

    except Exception as error:	
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

@api_view(['PUT'])
def ActualizarTipoServicio(request , pk=None):
    try: 
        if request.method == 'PUT':
            isTipoServicio = TipoServicio.objects.filter(id = pk).first()

            if isTipoServicio:
                tipoServicioSerializer = TipoServicioSerializer(isTipoServicio , data = request.data)

                if tipoServicioSerializer.is_valid():
                    tipoServicioSerializer.save()
                    isError = False
                    message = "El servicio fue actualizado con exito"

                    descripcion = f"El tipo de servicio por nombre {request.data['tipo_servicio']} fue modificado con exito"
                
                    RegistrarHistorial(2 , "tipo_servicio", pk, request.data['key_usuario'], descripcion)
            else:
                isError = True
                message = "El tipo servicio no se encuentra registrado en nuestra base de datos"
            
            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK) 

    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

@api_view(['PUT' , 'DELETE']) 
def TipoServicioEliminacionFiscaLogica(request , pk = None):
    try:
        isTipoServicio = TipoServicio.objects.filter(id = pk)
        keyEvento = 0
        keyUsuario = request.data['key_usuario']

        if isTipoServicio.first():
            if request.method == 'PUT':
                keyEstado = request.data['key_estado']

                isTipoServicio.update(key_estado_id = keyEstado)
                isError = False
                message = "El tipo de servicio fue restaurado con exito" if keyEstado == 1 else "El tipo servicio fue anulado con exito"
                keyEvento = 6 if keyEstado == 1 else 3

            elif request.method == 'DELETE':
                isTipoServicio.delete()
                keyEvento = 4
                isError = False
                message = "El tipo servicio fue eliminado con exito"
            
            RegistrarHistorial(keyEvento, 'tipo_servicio', pk , keyUsuario , message)
        else: 
            isError = True
            message = "El tipo servicio que desea actualizar o eliminar no se encuentra en nuestra base de datos"

        return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

@api_view(['POST'])
def ExportarTipoServicios(request):
    try:
        listaTipoServicio = ConsultaTipoServicio()
        
        if listaTipoServicio['is_error'] == False and len(listaTipoServicio['data']) != 0:
            df = pd.DataFrame(listaTipoServicio['data'])
            df = df.drop(columns = ['id' , 'key_estado', 'estado', 'color'])
            df.columns = ['TIPO SERVICIOS' , 'DESCRIPCIÓN']
        else: 
            columnsTipoServicios = [{'TIPO SERVICIOS' : '' , 'DESCRIPCIÓN': ''}]
            df = pd.DataFrame(columnsTipoServicios)

        crearExcel = CreateExcel(df , 'A1:B1', 'Tipo de servicios')

        if crearExcel['status'] == False:
            contexto = crearExcel['result']
            return contexto
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

#---------------------CRUD DE VETERINARIO ---------------------
@api_view(['GET'])
def  ListarVeterinarios(request):
    try:
        if request.method == 'GET':
            consulta = ConsultaVeterinario()
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return {'is_error': True , "message": str(error)}

def ConsultaVeterinario():
    try:
        query = f"""
        SELECT
        vet.id,
        vet.dni,
        CONCAT(vet.apellido , ' ', vet.nombre) as apellido_nombre,
        vet.nombre,
        vet.apellido,
        vet.direccion,
        vet.correo, 
        vet.num_cel,
        vet.key_estado_id as key_estado,
        vet.sexo,
        es.nombre as estado,
        es.icon,
        es.color
        FROM veterinario vet
        LEFT JOIN estado es on es.id = vet.key_estado_id
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}

@api_view(['POST'])
def AgregarVeterinario(request):
    try: 
        if request.method == 'POST':
            isVeterinario = Veterinario.objects.filter(dni = request.data['dni'])

            if isVeterinario.count() == 0:
                veterinarioSerializer = VeterinarioSerializer(data = request.data)

                if veterinarioSerializer.is_valid():
                    veterinarioSerializer.save()

                    keyVeterinario = veterinarioSerializer.data['id']
                    isError = False
                    message = "Informacion guarda con exito"

                    descripcion = f"El personal por nombre {request.data['nombre']} fue registrado con exito"

                    RegistrarHistorial(1 , "veterinario",keyVeterinario, request.data['key_usuario'], descripcion)
            else: 
                isError = True
                message = "La informacion ya se encuentra registrada en nuestra base de datos"
            
            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)

    except Exception as error:	
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

@api_view(['PUT'])
def ActualizarVeterinario(request , pk=None):
    try: 
        if request.method == 'PUT':
            isVeterinario = Veterinario.objects.filter(id = pk).first()

            if isVeterinario:
                veterinarioSerializer = VeterinarioSerializer(isVeterinario , data = request.data)

                if veterinarioSerializer.is_valid():
                    veterinarioSerializer.save()
                    isError = False
                    message = "El personal fue actualizado con exito"

                    descripcion = f"El personal por nombre {request.data['nombre']} fue modificado con exito"
                
                    RegistrarHistorial(2 , "veterinario", pk, request.data['key_usuario'], descripcion)
            else:
                isError = True
                message = "El personal no se encuentra registrado en nuestra base de datos"
            
            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK) 

    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

@api_view(['PUT' , 'DELETE']) 
def VeterinarioEliminacionFiscaLogica(request , pk = None):
    try:
        isVeterinario = Veterinario.objects.filter(id = pk)
        keyEvento = 0
        keyUsuario = request.data['key_usuario']

        if isVeterinario.first():
            if request.method == 'PUT':
                keyEstado = request.data['key_estado']

                isVeterinario.update(key_estado_id = keyEstado)
                isError = False
                message = "El personal fue restaurado con exito" if keyEstado == 1 else "El veterinario fue anulado con exito"
                keyEvento = 6 if keyEstado == 1 else 3

            elif request.method == 'DELETE':
                isVeterinario.delete()
                keyEvento = 4
                isError = False
                message = "El personal fue eliminado con exito"
            
            RegistrarHistorial(keyEvento, 'veterinario', pk , keyUsuario , message)
        else: 
            isError = True
            message = "El personal que desea actualizar o eliminar no se encuentra en nuestra base de datos"

        return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

@api_view(['POST'])
def ExportarVeterinario(request):
    try:
        listaVeterinarios = ConsultaVeterinario()
        
        if listaVeterinarios['is_error'] == False and len(listaVeterinarios['data']) != 0:
            df = pd.DataFrame(listaVeterinarios['data'])
            df = df.drop(columns = ['id' , 'key_estado', 'estado', 'color', 'icon', 'nombre','apellido'])
            df.columns = ['DNI' ,'APELLIDOS Y NOMBRES' , 'DIRECCION' , 'CORREO' , 'NRO. CELULAR', 'SEXO']
        else: 
            columnsVeterinarios = [{'DNI': '' , 'APELLIDOS Y NOMBRES' : '' , 'DIRECCION' : '' ,  'CORREO': '', 'NRO. CELULAR': '' , 'SEXO': ''}]
            df = pd.DataFrame(columnsVeterinarios)

        crearExcel = CreateExcel(df , 'A1:F1', 'Veterinarios')

        if crearExcel['status'] == False:
            contexto = crearExcel['result']
            return contexto
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

#---------------------CRUD DE CLIENTE-----------------------
@api_view(['POST'])
def ClientesFrecuentes(request):
    try:
        tipo = request.data['tipo']
        fechaInicio = request.data['fecha_inicio']
        fechaFin = request.data['fecha_fin']
        limite = request.data['limite']
        query = """
            WITH TotalCitas AS (
                SELECT
                    COUNT(id) AS totales_citas
                FROM
                    cita
                WHERE
                    fecha_inicio >= '{0}' AND 
	                fecha_inicio <= '{1}'
	            LIMIT {2}
            )
            SELECT
	            cl.dni as dni_cl,
	            CONCAT(cl.nombre, ' ' , cl.apellido) as nombre_completo_cliente,
                ROUND(COUNT(*) * 100.0 / (SELECT totales_citas FROM TotalCitas), 2) AS porcentaje,
	            COUNT(*) AS total_citas
            FROM cita ct
            LEFT JOIN cliente cl on cl.id = ct.key_cliente_id
            WHERE 
	            ct.fecha_inicio >= '{0}' AND 
	            ct.fecha_inicio <= '{1}'
            GROUP BY  
	            cl.dni , nombre_completo_cliente
            ORDER BY 
            	total_citas DESC
            LIMIT {2}
                """
        if tipo == 'anual':
             query = """
                    WITH TotalCitas AS (
                       SELECT
                           COUNT(id) AS totales_citas
                       FROM
                           cita
                       WHERE
                           DATE_PART('year', fecha_inicio) = DATE_PART('year', CURRENT_DATE)
	                   LIMIT 4
                    )
                    SELECT
	                    cl.dni as dni_cl,
	                    CONCAT(cl.nombre, ' ' , cl.apellido) as nombre_completo_cliente,
                        ROUND(COUNT(*) * 100.0 / (SELECT totales_citas FROM TotalCitas), 2) AS porcentaje,
	                    COUNT(*) AS total_citas
                    FROM cita ct
                    LEFT JOIN cliente cl on cl.id = ct.key_cliente_id
                    WHERE 
	                    DATE_PART('year', ct.fecha_inicio) = DATE_PART('year' , current_date)
                    GROUP BY  
	                    cl.dni , nombre_completo_cliente
                    ORDER BY 
                    	total_citas DESC
                    LIMIT {2}
                """
        with connections['default'].cursor() as cursor:
            cursor.execute(query.format(fechaInicio , fechaFin , limite))
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return  Response({'is_error': isError , 'data': data , "message": message} , status= status.HTTP_200_OK) 
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return  Response({'is_error': isError , 'data': data , "message": message} , status= status.HTTP_200_OK) 
    
@api_view(['POST'])
def TotalClientesNuevos(request):
    try:
        tipo = request.data['tipo']
        fechaInicio = request.data['fecha_inicio']
        fechaFin = request.data['fecha_fin']
        query = f"""
            SELECT 
                * 
            FROM fin_clientes_nuevos_2('{tipo}' , '{fechaInicio}' ,  '{fechaFin}')
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return  Response({'is_error': isError , 'data': data , "message": message} , status= status.HTTP_200_OK) 
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return  Response({'is_error': isError , 'data': data , "message": message} , status= status.HTTP_200_OK) 

@api_view(['POST'])
def TotalTiemposReg(request):
    try:
        tipo = request.data['tipo']
        fechaInicio = request.data['fecha_inicio']
        fechaFin = request.data['fecha_fin']
        query = f"""
                    SELECT 
                        * 
                    FROM fin_tiempo_registro('{tipo}' , '{fechaInicio}' ,  '{fechaFin}')
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return  Response({'is_error': isError , 'data': data , "message": message} , status= status.HTTP_200_OK) 
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return  Response({'is_error': isError , 'data': data , "message": message} , status= status.HTTP_200_OK) 

@api_view(['POST'])
def TotalIngresosCitas(request):
    try:
        tipo = request.data['tipo']
        fechaInicio = request.data['fecha_inicio']
        fechaFin = request.data['fecha_fin']
        print(fechaInicio , fechaFin)
        query = """
            WITH TotalCitas AS (
        SELECT
            COUNT(id) AS total_citas_totales
        FROM
            cita ct
        WHERE
            ct.fecha_inicio >= '{0}' AND 
         ct.fecha_inicio <= '{1}'
  )
           SELECT
                COUNT(*) AS totales_citas,
	            SUM(ser.precio) as ingresos,
                ROUND(COUNT(*) * 100.0 / (SELECT total_citas_totales FROM TotalCitas), 0) AS porcentaje,
	            ct.fecha_inicio
            FROM
                cita ct
            LEFT JOIN 
            	servicio ser on ser.id = ct.key_servicio_id
            WHERE
                 ct.fecha_inicio >= '{0}' AND 
            	 ct.fecha_inicio <= '{1}'
            GROUP BY  
            	ct.fecha_inicio
                """
        
        if tipo == 'anual':
            query = """
                    WITH TotalCitas AS (
                        SELECT
                            COUNT(id) AS total_citas_totales
                        FROM
                            cita
                        WHERE
                            DATE_PART('year', fecha_inicio) = DATE_PART('year', CURRENT_DATE)
                    )
                    SELECT
                        COUNT(*) AS totales_citas,
                    	SUM(ser.precio) as ingresos,
                    	ROUND(COUNT(*) * 100.0 / (SELECT total_citas_totales FROM TotalCitas), 2) AS porcentaje,
                    	DATE_TRUNC('month', ct.fecha_inicio) as fecha
                    FROM
                        cita ct
                    LEFT JOIN 
                    	servicio ser on ser.id = ct.key_servicio_id
                    WHERE
                        DATE_PART('year', ct.fecha_inicio) = DATE_PART('year', CURRENT_DATE)
                    GROUP BY  
                    	fecha
            """
        with connections['default'].cursor() as cursor:
            cursor.execute(query.format(fechaInicio , fechaFin))
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return  Response({'is_error': isError , 'data': data , "message": message} , status= status.HTTP_200_OK) 
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return  Response({'is_error': isError , 'data': data , "message": message} , status= status.HTTP_200_OK) 

@api_view(['POST'])
def TotalServiciosUtilizados(request):
    try:
        tipo = request.data['tipo']
        fechaInicio = request.data['fecha_inicio']
        fechaFin = request.data['fecha_fin']
        print(fechaInicio , fechaFin)
        query = """ 
            SELECT
             COUNT(ser.id) AS total_servicios,
	         ser.nombre_servicio
            FROM
             cita ct
            LEFT JOIN 
            	servicio ser on ser.id = ct.key_servicio_id
            WHERE
             ct.fecha_inicio >= '{0}' AND 
             ct.fecha_inicio <= '{1}'
            GROUP BY  
             ser.nombre_servicio
            ORDER BY 
                    total_servicios DESC
                """
        
        if tipo == 'anual':
            query = """
                SELECT
                    COUNT(ser.id) AS  total_servicios,
	                ser.nombre_servicio
                FROM
                    cita ct
                LEFT JOIN 
                	servicio ser on ser.id = ct.key_servicio_id
                WHERE
                    DATE_PART('year', ct.fecha_inicio) = DATE_PART('year', CURRENT_DATE)
                GROUP BY  
                    	ser.nombre_servicio
                ORDER BY 
                   total_servicios DESC
            """
        with connections['default'].cursor() as cursor:
            cursor.execute(query.format(fechaInicio , fechaFin))
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return  Response({'is_error': isError , 'data': data , "message": message} , status= status.HTTP_200_OK) 
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return  Response({'is_error': isError , 'data': data , "message": message} , status= status.HTTP_200_OK) 
    
@api_view(['POST'])
def TotalMascotasClientes(request):
    try:
        tipo = request.data['tipo']
        fechaInicio = request.data['fecha_inicio']
        fechaFin = request.data['fecha_fin']
        print(fechaInicio , fechaFin)
        query = """ 
                SELECT 
	                cl.dni ,
	                CONCAT(cl.nombre, ' ' , cl.apellido) as nombre_completo_cliente,
	                count(mas.id) AS total_mascota
                FROM
                    cliente cl
                LEFT JOIN 
                	mascota mas on mas.key_cliente_id = cl.id
                WHERE 
                	DATE(mas.fecha_registro) >='2024-03-21' AND DATE(mas.fecha_registro) <='2024-03-28'
                GROUP BY  
                	cl.dni , nombre_completo_cliente
                ORDER BY total_mascota DESC
                """
        
        if tipo == 'anual':
            query = """
                SELECT 
	                cl.dni ,
	                CONCAT(cl.nombre, ' ' , cl.apellido) as nombre_completo_cliente,
	                count(mas.id) AS total_mascota
                FROM
                    cliente cl
                LEFT JOIN 
                	mascota mas on mas.key_cliente_id = cl.id
                WHERE 
                	DATE_PART('year', mas.fecha_registro) = DATE_PART('year', CURRENT_DATE)
                GROUP BY  
                	cl.dni , nombre_completo_cliente
                ORDER BY total_mascota DESC
            """
        with connections['default'].cursor() as cursor:
            cursor.execute(query.format(fechaInicio , fechaFin))
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return  Response({'is_error': isError , 'data': data , "message": message} , status= status.HTTP_200_OK) 
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return  Response({'is_error': isError , 'data': data , "message": message} , status= status.HTTP_200_OK) 

def ConsultarClientes():
    try:
        query = f"""
        SELECT
		cl.id,
        cl.dni,
        CONCAT(cl.dni , '-', cl.nombre) as dni_nombre,
        CONCAT(cl.apellido , ' ', cl.nombre) as apellido_nombre,
        cl.nombre,
        cl.apellido,
        cl.direccion,
        cl.correo, 
        cl.num_cel,
        cl.key_estado_id as key_estado,
        cl.sexo,
        es.nombre as estado,
        es.icon,
        es.color
        FROM cliente cl
        LEFT JOIN estado es on es.id = cl.key_estado_id
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}

@api_view(['GET'])
def  ListarCientes(request):
    try:
        if request.method == 'GET':
            consulta = ConsultarClientes()
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return {'is_error': True , "message": str(error)}

@api_view(['POST'])
def AgregarClientes(request):
    try: 
        if request.method == 'POST':
            isClientes = Cliente.objects.filter(dni = request.data['dni'])
            if isClientes.count() == 0:
                ClienteSerializer = ClientesSerializer(data = request.data)

                if ClienteSerializer.is_valid():
                    ClienteSerializer.save()

                    keyCliente = ClienteSerializer.data['id']
                    isError = False
                    message = "Informacion guarda con exito"

                    descripcion = f"El cliente por nombre {request.data['nombre']} fue registrado con exito"

                    RegistrarHistorial(1 , "cliente",keyCliente, request.data['key_usuario'], descripcion)
                else:
                    keyCliente = 0
                    isError = True
                    message = f"error de lectura por lo siguiente: {ClienteSerializer.errors}"
            else:
                keyCliente = 0 
                isError = True
                message = "La informacion ya se encuentra registrada en nuestra base de datos"
            
            return Response({"is_error": isError, "message" : message , "key_cliente" : keyCliente} ,  status= status.HTTP_200_OK)

    except Exception as error:	
        print(error)
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

@api_view(['PUT'])
def ActualizarClientes(request , pk=None):
    try: 
        if request.method == 'PUT':
            isClientes = Cliente.objects.filter(id = pk).first()

            if isClientes:
                clientesSerializer =  ClientesSerializer(isClientes , data = request.data)

                if clientesSerializer.is_valid():
                    clientesSerializer.save()
                    isError = False
                    message = "El cliente fue actualizado con exito"

                    descripcion = f"El cliente por nombre {request.data['nombre']} fue modificado con exito"
                
                    RegistrarHistorial(2 , "cliente", pk, request.data['key_usuario'], descripcion)
            else:
                isError = True
                message = "El cliente no se encuentra registrado en nuestra base de datos"
            
            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK) 

    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 
    
@api_view(['PUT' , 'DELETE']) 
def ClienteEliminacionFiscaLogica(request , pk = None):
    try:
        isCliente = Cliente.objects.filter(id = pk)
        keyEvento = 0
        keyUsuario = request.data['key_usuario']

        if isCliente.first():
            if request.method == 'PUT':
                keyEstado = request.data['key_estado']

                isCliente.update(key_estado_id = keyEstado)
                isError = False
                message = "El cliente fue restaurado con exito" if keyEstado == 1 else "El cliente fue anulado con exito"
                keyEvento = 6 if keyEstado == 1 else 3

            elif request.method == 'DELETE':
                isCliente.delete()
                keyEvento = 4
                isError = False
                message = "El cliente fue eliminado con exito"
            
            RegistrarHistorial(keyEvento, 'cliente', pk , keyUsuario , message)
        else: 
            isError = True
            message = "El cliente que desea actualizar o eliminar no se encuentra en nuestra base de datos"

        return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

@api_view(['POST'])
def ExportarCliente(request):
    try:
        listaCliente = ConsultarClientes()
        
        if listaCliente['is_error'] == False and len(listaCliente['data']) != 0:
            df = pd.DataFrame(listaCliente['data'])
            df = df.drop(columns = ['id' , 'key_estado', 'estado', 'color', 'icon', 'nombre','apellido' , 'dni_nombre'])
            df.columns = ['DNI' ,'APELLIDOS Y NOMBRES' , 'DIRECCION' , 'CORREO' , 'NRO. CELULAR', 'SEXO']
        else: 
            columnsCliente = [{'DNI': '' , 'APELLIDOS Y NOMBRES' : '' , 'DIRECCION' : '' ,  'CORREO': '', 'NRO. CELULAR': '' , 'SEXO': ''}]
            df = pd.DataFrame(columnsCliente)

        crearExcel = CreateExcel(df , 'A1:F1', 'Veterinarios')

        if crearExcel['status'] == False:
            contexto = crearExcel['result']
            return contexto
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

#---------------------CRUD DE RAZA-----------------------
def ConsultarRaza():
    try:
        query = f"""
            SELECT 
            rz.id,
            rz.nombre_raza,
            rz.descripcion,
            es.id as key_estado,
            es.nombre as estado,
            es.color
            FROM raza rz
            LEFT JOIN estado es on es.id = rz.key_estado_id
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}
    
@api_view(['GET'])
def  ListarRaza(request):
    try:
        if request.method == 'GET':
            consulta = ConsultarRaza()
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return {'is_error': True , "message": str(error)}
    
@api_view(['POST'])
def AgregarRaza(request):
    try: 
        if request.method == 'POST':
            isRaza = Raza.objects.filter(nombre_raza = request.data['nombre_raza'])
            if isRaza.count() == 0:
                razaSerializer = RazaSerializer(data = request.data)

                if razaSerializer.is_valid():
                    razaSerializer.save()

                    keyRaza = razaSerializer.data['id']
                    isError = False
                    message = "Informacion guarda con exito"

                    descripcion = f"La raza por nombre {request.data['nombre_raza']} fue registrado con exito"

                    RegistrarHistorial(1 , "raza",keyRaza, request.data['key_usuario'], descripcion)
                else:
                    isError = True
                    message = f"error de lectura por lo siguiente: {razaSerializer.errors}"
            else: 
                isError = True
                message = "La informacion ya se encuentra registrada en nuestra base de datos"
            
            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)

    except Exception as error:	
        print(error)
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 
    
@api_view(['PUT'])
def ActualizarRaza(request , pk=None):
    try: 
        if request.method == 'PUT':
            isRaza = Raza.objects.filter(id = pk).first()

            if isRaza:
                razaSerializer =  RazaSerializer(isRaza , data = request.data)

                if razaSerializer.is_valid():
                    razaSerializer.save()
                    isError = False
                    message = "los datos fueron actualizado con exito"

                    descripcion = f"La raza por nombre {request.data['nombre_raza']} fue modificado con exito"
                
                    RegistrarHistorial(2 , "raza", pk, request.data['key_usuario'], descripcion)
                else:
                    isError = True
                    message = f"error de lectura por lo siguiente: {razaSerializer.errors}"
            else:
                isError = True
                message = "La raza no se encuentra registrado en nuestra base de datos"
            
            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK) 

    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

@api_view(['PUT' , 'DELETE']) 
def RazaEliminacionFiscaLogica(request , pk = None):
    try:
        isRaza = Raza.objects.filter(id = pk)
        keyEvento = 0
        keyUsuario = request.data['key_usuario']

        if isRaza.first():
            if request.method == 'PUT':
                keyEstado = request.data['key_estado']

                isRaza.update(key_estado_id = keyEstado)
                isError = False
                message = "Los datos fueron restaurado con exito" if keyEstado == 1 else "Los datos fueron anulado con exito"
                keyEvento = 6 if keyEstado == 1 else 3

            elif request.method == 'DELETE':
                isRaza.delete()
                keyEvento = 4
                isError = False
                message = "Los datos fueron eliminados con exito"
            
            RegistrarHistorial(keyEvento, 'raza', pk , keyUsuario , message)
        else: 
            isError = True
            message = "La raza que desea actualizar o eliminar no se encuentra en nuestra base de datos"

        return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

@api_view(['POST'])
def ExportarRazas(request):
    try:
        listaRaza = ConsultarRaza()
        
        if listaRaza['is_error'] == False and len(listaRaza['data']) != 0:
            df = pd.DataFrame(listaRaza['data'])
            df = df.drop(columns = ['id' , 'key_estado', 'estado', 'color'])
            df.columns = ['RAZAS' ,'DESCRIPCIÓN']
        else: 
            columns = [{'RAZAS': '' , 'DESCRIPCIÓN' : ''}]
            df = pd.DataFrame(columns)

        crearExcel = CreateExcel(df , 'A1:B1', 'Razas')

        if crearExcel['status'] == False:
            contexto = crearExcel['result']
            return contexto
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

#---------------------CRUD DE TIPO DE MASCOTA-----------------------
def ConsultarTipoMascota():
    try:
        query = f"""
            SELECT 
            tp.id,
            tp.tipo,
            tp.descripcion,
            es.id as key_estado,
            es.nombre as estado,
            es.color
            FROM tipo_mascota tp
            LEFT JOIN estado es on es.id = tp.key_estado_id
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}

@api_view(['GET'])
def  ListarTipoMascota(request):
    try:
        if request.method == 'GET':
            consulta = ConsultarTipoMascota()
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return {'is_error': True , "message": str(error)}

@api_view(['POST'])
def AgregarTipoMascota(request):
    try: 
        if request.method == 'POST':
            isTipoMascota = TipoMascota.objects.filter(tipo = request.data['tipo'])
            if isTipoMascota.count() == 0:
                tipoMascotaSerializer = TipoMascotaSerializer(data = request.data)

                if tipoMascotaSerializer.is_valid():
                    tipoMascotaSerializer.save()

                    key = tipoMascotaSerializer.data['id']
                    isError = False
                    message = "Informacion guarda con exito"

                    descripcion = f"El tipo de mascota por nombre {request.data['tipo']} fue registrado con exito"

                    RegistrarHistorial(1 , "tipo_mascota",key, request.data['key_usuario'], descripcion)
                else:
                    isError = True
                    message = f"error de lectura por lo siguiente: {tipoMascotaSerializer.errors}"
            else: 
                isError = True
                message = "La informacion ya se encuentra registrada en nuestra base de datos"
            
            return Response({"is_error": isError, "message" : message } ,  status= status.HTTP_200_OK)

    except Exception as error:	
        print(error)
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK)
    
@api_view(['PUT'])
def ActualizarTipoMascota(request , pk=None):
    try: 
        if request.method == 'PUT':
            isTipoMascota = TipoMascota.objects.filter(id = pk).first()

            if isTipoMascota:
                tipoMascotaSerializer =  TipoMascotaSerializer(isTipoMascota , data = request.data)

                if tipoMascotaSerializer.is_valid():
                    tipoMascotaSerializer.save()
                    isError = False
                    message = "los datos fueron actualizado con exito"

                    descripcion = f"El tipo de mascota por nombre {request.data['tipo']} fue modificado con exito"
                
                    RegistrarHistorial(2 , "tipo_mascota", pk, request.data['key_usuario'], descripcion)
                else:
                    isError = True
                    message = f"error de lectura por lo siguiente: {tipoMascotaSerializer.errors}"
            else:
                isError = True
                message = "El tipo de mascota no se encuentra registrado en nuestra base de datos"
            
            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK) 

    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK)

@api_view(['PUT' , 'DELETE']) 
def TipoMascotaEliminacionFiscaLogica(request , pk = None):
    try:
        isTipoMascota = TipoMascota.objects.filter(id = pk)
        keyEvento = 0
        keyUsuario = request.data['key_usuario']

        if isTipoMascota.first():
            if request.method == 'PUT':
                keyEstado = request.data['key_estado']

                isTipoMascota.update(key_estado_id = keyEstado)
                isError = False
                message = "Los datos fueron restaurado con exito" if keyEstado == 1 else "Los datos fueron anulado con exito"
                keyEvento = 6 if keyEstado == 1 else 3

            elif request.method == 'DELETE':
                isTipoMascota.delete()
                keyEvento = 4
                isError = False
                message = "Los datos fueron eliminados con exito"
            
            RegistrarHistorial(keyEvento, 'tipo_mascota', pk , keyUsuario , message)
        else: 
            isError = True
            message = "El tipo de mascota que desea actualizar o eliminar no se encuentra en nuestra base de datos"

        return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

@api_view(['POST'])
def ExportarTipoMascota(request):
    try:
        listaMascota = ConsultarTipoMascota()
        
        if listaMascota['is_error'] == False and len(listaMascota['data']) != 0:
            df = pd.DataFrame(listaMascota['data'])
            df = df.drop(columns = ['id' , 'key_estado', 'estado', 'color'])
            df.columns = ['TIPO' ,'DESCRIPCIÓN']
        else: 
            columns = [{'TIPO': '' , 'DESCRIPCIÓN' : ''}]
            df = pd.DataFrame(columns)

        crearExcel = CreateExcel(df , 'A1:B1', 'Tipo de mascota')

        if crearExcel['status'] == False:
            contexto = crearExcel['result']
            return contexto
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

#---------------------CRUD DE MASCOTA-----------------------
def ConsultarMascota():
    try:
        query = f"""
            SELECT 
            mas.id,
            mas.nombre as nombre_mascota,
            mas.fecha_nacimiento,
            mas.sexo,
            mas.color,
            es.id as key_estado,
            es.nombre as estado,
            es.color as color_estado,
            rz.id as key_raza,
            rz.nombre_raza,
            tp.id as key_tipo,
            tp.tipo,
            cl.id as key_cliente,
            cl.dni,
            CONCAT(cl.apellido , ' ', cl.nombre) as apellido_nombre
            FROM mascota mas
            LEFT JOIN estado es on es.id = mas.key_estado_id
            LEFT JOIN cliente cl on cl.id = mas.key_cliente_id
            LEFT JOIN raza rz on rz.id = mas.key_raza_id
            LEFT JOIN tipo_mascota tp on tp.id = mas.key_tipo_mascota_id
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}

@api_view(['GET'])
def  ListarMacotas(request):
    try:
        if request.method == 'GET':
            consulta = ConsultarMascota()
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return {'is_error': True , "message": str(error)}
    
@api_view(['POST'])
def AgregarMascota(request):
    try: 
        if request.method == 'POST':
            fechaActual = datetime.now().strftime('%Y/%m/%d')

            fechaNacimiento = datetime.strptime(request.data['fecha_nacimiento'] , "%Y-%m-%dT%H:%M:%S.%fZ").strftime('%Y/%m/%d')

            isMascota = Mascota.objects.filter(Q(nombre = request.data['nombre']) , Q(key_cliente = request.data['key_cliente']))

            if isMascota.count() == 0:
                if fechaNacimiento <= fechaActual: 
                    mascotaSerializer = MascotaSerializer(data = request.data)

                    if mascotaSerializer.is_valid():

                        mascotaSerializer.save()

                        key = mascotaSerializer.data['id']
                        isError = False
                        message = "Informacion guarda con exito"

                        descripcion = f"La mascota por nombre {request.data['nombre']} fue registrado con exito"

                        RegistrarHistorial(1 , "mascota",key, request.data['key_usuario'], descripcion)
                    else:
                        key = 0
                        isError = True
                        message = f"error de lectura por lo siguiente: {mascotaSerializer.errors}"
                else:
                    key = 0
                    isError = True
                    message = "La fecha de nacimiento de la mascota no puede ser mayor a la actual"
            else: 
                key = 0
                isError = True
                message = "La mascota ya se encuentra registrada en nuestra base de datos"
            
            return Response({"is_error": isError, "message" : message , 'key_mascota' : key} ,  status= status.HTTP_200_OK)

    except Exception as error:	
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK)

@api_view(['PUT'])
def ActualizarMascota(request , pk=None):
    try: 
        if request.method == 'PUT':
            isMascota = Mascota.objects.filter(id = pk).first()

            if isMascota:
                mascotaSerializer =  MascotaSerializer(isMascota , data = request.data)

                if mascotaSerializer.is_valid():
                    mascotaSerializer.save()
                    isError = False
                    message = "los datos fueron actualizado con exito"

                    descripcion = f"La mascota por nombre {request.data['nombre']} fue modificado con exito"
                
                    RegistrarHistorial(2 , "mascota", pk, request.data['key_usuario'], descripcion)
                else:
                    isError = True
                    message = f"error de lectura por lo siguiente: {mascotaSerializer.errors}"
            else:
                isError = True
                message = "La mascota no se encuentra registrado en nuestra base de datos"
            
            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK) 

    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK)
    
@api_view(['PUT' , 'DELETE']) 
def MascotaEliminacionFiscaLogica(request , pk = None):
    try:
        isMascota = Mascota.objects.filter(id = pk)
        keyEvento = 0
        keyUsuario = request.data['key_usuario']

        if isMascota.first():
            if request.method == 'PUT':
                keyEstado = request.data['key_estado']

                isMascota.update(key_estado_id = keyEstado)
                isError = False
                message = "Los datos fueron restaurado con exito" if keyEstado == 1 else "Los datos fueron anulado con exito"
                keyEvento = 6 if keyEstado == 1 else 3

            elif request.method == 'DELETE':
                isMascota.delete()
                keyEvento = 4
                isError = False
                message = "Los datos fueron eliminados con exito"
            
            RegistrarHistorial(keyEvento, 'mascota', pk , keyUsuario , message)
        else: 
            isError = True
            message = "La mascota que desea actualizar o eliminar no se encuentra en nuestra base de datos"

        return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

@api_view(['POST'])
def ExportarMascota(request):
    try:
        listaMascota = ConsultarMascota()
        
        if listaMascota['is_error'] == False and len(listaMascota['data']) != 0:
            df = pd.DataFrame(listaMascota['data'])
            df = df.drop(columns = ['id' , 'key_estado', 'estado', 'color_estado' , 'key_cliente', 'key_raza' , 'key_tipo'])
            df.columns = ['MASCOTA' ,'FECHA NACIMIENTO' , 'SEXO' , 'COLOR', 'RAZA' , 'TIPO', 'CLIENTE']
        else: 
            columns = [{'MASCOTA' : '' ,'FECHA NACIMIENTO' : '' , 'SEXO' : '' , 'COLOR' : '', 'RAZA' : '', 'TIPO': '', 'CLIENTE' : ''}]
            df = pd.DataFrame(columns)

        crearExcel = CreateExcel(df , 'A1:G1', 'Mascota')

        if crearExcel['status'] == False:
            contexto = crearExcel['result']
            return contexto
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

#---------------------CRUD DE TIPO DE CONSULTA-----------------------
def ConsultarTipoCita():
    try:
        query = f"""
            SELECT 
            tc.id,
            tc.tipo_cita,
            tc.descripcion,
            es.id as key_estado,
            es.nombre as estado,
            es.color
            FROM tipo_cita tc 
            LEFT JOIN estado es on es.id = tc.key_estado_id
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}

@api_view(['GET'])
def  ListarTipoCita(request):
    try:
        if request.method == 'GET':
            consulta = ConsultarTipoCita()
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return {'is_error': True , "message": str(error)}
    
#---------------------CRUD DE CONSULTA-----------------------  
@api_view(['GET'])
def TotalCitasEstados(request):
    try:
        query = f"""
               SELECT 
                    es.id as estado_id,
                    es.nombre as nombre_estado,
                    es.color,
                    es.icon,
                    COUNT(c.id) as total_citas
                FROM 
                    public.cita c
                INNER JOIN 
                    estado es ON c.key_estado_id = es.id
                GROUP BY 
                    es.id, es.nombre, es.color, es.icon;
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return Response({'is_error': isError , 'result': data , "message": message} , status= status.HTTP_200_OK)
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return Response({'is_error': isError , 'result': data , "message": message} , status= status.HTTP_200_OK)

def ConsultarCita():
    try:
        query = f"""
                SELECT * FROM fn_listar_cita(0)
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}

def ConsultarCitaId(id):
    try:
        query = f"""
                SELECT * FROM fn_listar_cita({id})
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}

@api_view(['GET'])
def  ListarCitaId(request , pk=None):
    try:
        if request.method == 'GET':
            consulta = ConsultarCitaId(pk)
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return {'is_error': True , "message": str(error)}
    
@api_view(['GET'])
def  ListarCita(request):
    try:
        if request.method == 'GET':
            consulta = ConsultarCita()
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return {'is_error': True , "message": str(error)}

@api_view(['POST'])    
def AgregarCita(request):
    try: 
        if request.method == 'POST':
            fechaInicio = request.data['fecha_inicio'] 

            horaInicio = request.data['hora_inicio']
            horaFin = request.data['hora_fin']
            keyVeterinario = request.data['key_veterinario']

            isValidHorario =  isValidarHorario(fechaInicio , horaInicio , horaFin ,keyVeterinario)

            if isValidHorario['data']['count'] == 0:
                citaSerializer = CitasSerializer(data = request.data)

                if citaSerializer.is_valid():
                    citaSerializer.save()

                    key = citaSerializer.data['id']
                    isError = False
                    message = 'La cita fue programada con exito'

                    RegistrarHistorial(1 , "cita", key, request.data['key_usuario'], message)
                else:
                    isError = True
                    message = f'error de lectura, por lo siguiente: {citaSerializer.errors}'

            else:
                isError = True
                message = 'El veterinario esta ocupado con otra cita, seleccione otro(a) o cambie el horario'

            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)
    except Exception as error:
        print(error)
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK)

@api_view(['PUT'])
def ActualizarCita(request , pk=None):
    try: 
        if request.method == 'PUT':
            fechaInicio = request.data['fecha_inicio'] 

            horaInicio = request.data['hora_inicio']
            horaFin = request.data['hora_fin']
            keyVeterinario = request.data['key_veterinario']

            isValidHorario =  isValidarHorario(fechaInicio , horaInicio , horaFin ,keyVeterinario)

            isCita = Cita.objects.filter(id = pk).first()

            if isCita:
                if isValidHorario['data']['count'] == 0:
                    citaSerializer = CitasSerializer(isCita ,  data = request.data)

                    if citaSerializer.is_valid():
                        citaSerializer.save()

                        key = citaSerializer.data['id']
                        isError = False
                        message = 'La cita actualizada con exito'

                        RegistrarHistorial(2 , "cita", key, request.data['key_usuario'], message)
                    else:
                        isError = True
                        message = f'error de lectura, por lo siguiente: {citaSerializer.errors}'

                else:
                    isError = True
                    message = 'El veterinario esta ocupado con otra cita, seleccione otro(a) o cambie el horario'
            else:
                isError = True
                message = 'La cita no se encuentra registrado en nuestra base de datos'
            
            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK) 

    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK)

@api_view(['PUT' , 'DELETE']) 
def CitaEliminacionFiscaLogica(request , pk = None):
    try:
        isCita  = Cita.objects.filter(id = pk)
        keyEvento = 0
        keyUsuario = request.data['key_usuario']

        if isCita.first():
            if request.method == 'PUT':
                keyEstado = request.data['key_estado']

                isCita.update(key_estado_id = keyEstado , motivo_cancelacion = request.data['motivo_cancelacion'])
                isError = False
                message = "El estado de la cita fue cambiada con exito" if keyEstado == 8 else "La cita fue cancelada con exito"
                keyEvento = 6 if keyEstado == 1 else 3

            elif request.method == 'DELETE':
                isCita.delete()
                keyEvento = 4
                isError = False
                message = "Los datos fueron eliminados con exito"
            
            RegistrarHistorial(keyEvento, 'cita', pk , keyUsuario , message)
        else: 
            isError = True
            message = "La cita que desea actualizar o eliminar no se encuentra en nuestra base de datos"

        return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

@api_view(['PUT'])
def ReprogramarCita(request , pk = None):
    try:
        if request.method == "PUT":
            fechaInicio = request.data['fecha_inicio'] 
            horaInicio = request.data['hora_inicio']
            horaFin = request.data['hora_fin']
            keyVeterinario = request.data['key_veterinario']

            isValidHorario =  isValidarHorario(fechaInicio , horaInicio , horaFin ,keyVeterinario)

            if isValidHorario['data']['count'] == 0:
                isCita  = Cita.objects.filter(id = pk)
                if isCita.first():
                    isCita.update(fecha_inicio = fechaInicio , hora_inicio = horaInicio , hora_fin = horaFin , key_veterinario = keyVeterinario )

                    isError = False
                    message = "Se reprogramo con exito la cita"
                else:
                    isError = True
                    message = "La cita que desea reprogramar no se encuentra en nuestra base de datos"

            else:
                isError = True
                message = 'No se puede reprogramar ya que el horario o veterinario se encuentra ocupado, seleccione otro(a) o cambie el horario'
            
            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} , status= status.HTTP_200_OK)

def isValidarHorario(fechaInicio , horaInicio , horaFin, keyVeter):
    fechaHoraInicio = f"{fechaInicio} {horaInicio}"
    fechaHoraFin = f"{fechaInicio} {horaFin}"

    try:

        query = f"""
        SELECT 
	        COUNT(id) 
        FROM 
        	cita
        WHERE 
        	'{fechaHoraInicio}' >= CONCAT(fecha_inicio, ' ', hora_inicio) AND
        	'{fechaHoraFin}' <= CONCAT(fecha_inicio, ' ', hora_fin) AND
        	key_veterinario_id = {keyVeter}
        """

        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado[0]
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        print(error)
        return {"is_error": True, "message" : str(error)}


#---------------------CRUD DE PREGUNTAS FRECUENTES-----------------------
def ConsultarPreguntaFrecuntes():
    try:
        query = f"""
            SELECT
            pf.id, 
            pf.asunto,
            pf.descripcion,
            es.id as key_estado,
            es.nombre as estado,
            es.color
            FROM pregunta_frecuente pf
            LEFT JOIN estado es on es.id = pf.key_estado_id
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}

@api_view(['GET'])
def  ListarPreguntaFrecuntes(request):
    try:
        if request.method == 'GET':
            consulta = ConsultarPreguntaFrecuntes()
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return {'is_error': True , "message": str(error)}

@api_view(['POST'])
def AgregarPreguntaFrecuntes(request):
    try: 
        if request.method == 'POST':
            isPreguntaFrecuntes = PreguntaFrecuentes.objects.filter(asunto = request.data['asunto'])
            if isPreguntaFrecuntes.count() == 0:
                preguntaFrecuenteSerializer = PreguntaFrecuentesSerializer(data = request.data)

                if preguntaFrecuenteSerializer.is_valid():
                    preguntaFrecuenteSerializer.save()

                    key = preguntaFrecuenteSerializer.data['id']
                    isError = False
                    message = "Informacion guarda con exito"

                    descripcion = f"el registro por asunto {request.data['asunto']} fue guardado con exito"

                    RegistrarHistorial(1 , "pregunta_frecuente",key, request.data['key_usuario'], descripcion)
                else:
                    isError = True
                    message = f"error de lectura por lo siguiente: {preguntaFrecuenteSerializer.errors}"
            else: 
                isError = True
                message = "La informacion ya se encuentra registrada en nuestra base de datos"
            
            return Response({"is_error": isError, "message" : message } ,  status= status.HTTP_200_OK)

    except Exception as error:	
        print(error)
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK)
    
@api_view(['PUT'])
def ActualizarPreguntasFrecuentes(request , pk=None):
    try: 
        if request.method == 'PUT':
            isPreguntaFrecuntes = PreguntaFrecuentes.objects.filter(id = pk).first()

            if isPreguntaFrecuntes:
                preguntaFrecuenteSerializer =  PreguntaFrecuentesSerializer(isPreguntaFrecuntes , data = request.data)

                if preguntaFrecuenteSerializer.is_valid():
                    preguntaFrecuenteSerializer.save()
                    isError = False
                    message = "los datos fueron actualizado con exito"

                    descripcion = f"El asunto por nombre {request.data['asunto']} fue modificado con exito"
                
                    RegistrarHistorial(2 , "pregunta_frecuente", pk, request.data['key_usuario'], descripcion)
                else:
                    isError = True
                    message = f"error de lectura por lo siguiente: {preguntaFrecuenteSerializer.errors}"
            else:
                isError = True
                message = "Los datos a consultar no se encuentra registrado en nuestra base de datos"
            
            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK) 

    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK)

@api_view(['PUT' , 'DELETE']) 
def PreguntasFrecuentesEliminacionFiscaLogica(request , pk = None):
    try:
        isPreguntaFrecuntes = PreguntaFrecuentes.objects.filter(id = pk)
        keyEvento = 0
        keyUsuario = request.data['key_usuario']

        if isPreguntaFrecuntes.first():
            if request.method == 'PUT':
                keyEstado = request.data['key_estado']

                isPreguntaFrecuntes.update(key_estado_id = keyEstado)
                isError = False
                message = "Los datos fueron restaurado con exito" if keyEstado == 1 else "Los datos fueron anulado con exito"
                keyEvento = 6 if keyEstado == 1 else 3

            elif request.method == 'DELETE':
                isPreguntaFrecuntes.delete()
                keyEvento = 4
                isError = False
                message = "Los datos fueron eliminados con exito"
            
            RegistrarHistorial(keyEvento, 'pregunta_frecuente', pk , keyUsuario , message)
        else: 
            isError = True
            message = "Los datos a consultar no se encuentra registrado en nuestra base de datos"

        return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

@api_view(['POST'])
def ExportarPreguntasFrecuentes(request):
    try:
        listaPreguntas = ConsultarPreguntaFrecuntes()
        
        if listaPreguntas['is_error'] == False and len(listaPreguntas['data']) != 0:
            df = pd.DataFrame(listaPreguntas['data'])
            df = df.drop(columns = ['id' , 'key_estado', 'estado', 'color'])
            df.columns = ['ASUNTO' ,'DESCRIPCIÓN']
        else: 
            columns = [{'ASUNTO': '' , 'DESCRIPCIÓN' : ''}]
            df = pd.DataFrame(columns)

        crearExcel = CreateExcel(df , 'A1:B1', 'Preguntas frecuentes')

        if crearExcel['status'] == False:
            contexto = crearExcel['result']
            return contexto
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK) 

#---------------------CRUD DE USUARIOS-----------------------
def IsVerificarUser(nombreCampo , valorCampo):
    try:
        query = """
                SELECT 
                	id, 
                	document_number,
                	last_login,
                	username, 
                	first_name, 
                	last_name, 
                	email,
                	status_id
                FROM 
                	public.usuario
                WHERE 
	                {0} = '{1}'
        """.format(nombreCampo, valorCampo)

        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            result = ConvertirQueryADiccionarioDato(cursor)

            if(len(result) != 0): 
                isError = False
                message = "Consulta ejecutada con exito"
            else:
                isError = True
                message = "Sin resultado"

        return {"is_error": isError, "message" : message , "result": result}
    except Exception as error:
        return {"is_error": True, "message" : str(error) ,  "result": []}
    
def ConsultarUsuarios():
    try:
        query = f"""
                SELECT
                    us.id,
                    us.document_number,
                    us.first_name as nombre,
                    us.last_name as apellido,
                    us.username as usuario,
                    us.email as correo,
	                us.date_joined as fecha_registro,
	                to_char(timezone('America/Lima',  us.last_login), 'DD/MM/YYYY HH24:MI:SS') as ultimo_acceso,
                    COALESCE(cl.sexo, vt.sexo, '') as sexo,
                    COALESCE(cl.direccion, vt.direccion, '') as direccion,
                    COALESCE(cl.num_cel, vt.num_cel, '') as num_cel,
	                es.id as key_estado,
                    es.nombre as estado, 
                    es.color,
	                tp.id as key_tipo_usuario,
	                tp.tipo_usuario
                FROM 
                    usuario us
                LEFT JOIN 
                    cliente cl ON us.user_type_id = 3 AND cl.dni = us.document_number
                LEFT JOIN 
                    veterinario vt ON us.user_type_id = 2 AND vt.dni = us.document_number
                LEFT JOIN 
                	estado es on es.id = us.status_id
                LEFT JOIN 
                	tipo_usuario tp on tp.id = us.user_type_id
                """
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}

def consultaUsuarioId(dni):
    try:
        query ="""
                SELECT
                    us.id,
                    us.document_number,
                    us.first_name as nombre,
                    us.last_name as apellido,
                    us.username as usuario,
                    us.email as correo,
	                us.date_joined as fecha_registro,
	                to_char(timezone('America/Lima',  us.last_login), 'DD/MM/YYYY HH24:MI:SS') as ultimo_acceso,
                    COALESCE(cl.sexo, vt.sexo, '') as sexo,
                    COALESCE(cl.direccion, vt.direccion, '') as direccion,
                    COALESCE(cl.num_cel, vt.num_cel, '') as num_cel,
	                es.id as key_estado,
                    es.nombre as estado, 
                    es.color,
	                tp.id as key_tipo_usuario,
	                tp.tipo_usuario
                FROM 
                    usuario us
                LEFT JOIN 
                    cliente cl ON us.user_type_id = 3 AND cl.dni = us.document_number
                LEFT JOIN 
                    veterinario vt ON us.user_type_id = 2 AND vt.dni = us.document_number
                LEFT JOIN 
                	estado es on es.id = us.status_id
                LEFT JOIN 
                	tipo_usuario tp on tp.id = us.user_type_id
                WHERE 
                    us.document_number = '{0}'
                """.format(dni)
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}


@api_view(['GET'])
def ListarUsuarioId(request , dni=None):
    try:
        if request.method == 'GET':
            consulta = consultaUsuarioId(dni)
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return {'is_error': True , "message": str(error)}

@api_view(['GET'])
def ListarUsuario(request):
    try:
        if request.method == 'GET':
            consulta = ConsultarUsuarios()
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return {'is_error': True , "message": str(error)}
    
@api_view(['POST'])
def AgregarUsuario(request):
    try:
        if request.method == 'POST': 
            request.data['password'] = make_password(request.data['password'])
            usuarioSerializer = UsuarioSerializer(data = request.data)

            if usuarioSerializer.is_valid(): 
                usuarioSerializer.save()

                key = usuarioSerializer.data['id']
                isError = False
                message = "Se registro con exito el usuario"

                descripcion = "el usuario fue registrado con exito"

                RegistrarHistorial(1 , "usuario",key, request.data['key_usuario'], descripcion)
            else:
                isError = True
                message = [str(items[0])  for index ,items in usuarioSerializer.errors.items()][0]

                #message = f"error de lectura por lo siguiente: {menssage[0]}"

            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK)

@api_view(['PUT'])
def ActualizarUsuario(request , pk=None):
    try:
        if request.method == 'PUT':
            isUsuario = Usuario.objects.filter(id = pk).first()

            if isUsuario:
                request.data['password'] = make_password(request.data['password'])

                usuarioSerializer = UsuarioSerializer(isUsuario , data = request.data)

                if usuarioSerializer.is_valid():
                    usuarioSerializer.save()
                    isError = False
                    message = "Los datos fueron actualizado con exito"

                    descripcion = f"El usuario {request.data['username']} sus datos fueron actualizados con exito"

                    RegistrarHistorial(2 , "usuario", pk, request.data['key_usuario'], descripcion)
                else:
                    isError = True
                    message = f"error de lectura por lo siguiente: {usuarioSerializer.errors}"
            else:
                isError = True
                message ="El usuario no se encuetra registrado en nuestra base de datos"

            return Response({"is_error": isError, "message" : message } , status= status.HTTP_200_OK)

    except Exception as error:
        return Response({"is_error": True, "message" : str(error) } , status= status.HTTP_200_OK)

@api_view(['PUT'])
def ActualizarPerfil(request , id=None):  
    try:
        if request.method == 'PUT':
            isUsuario = Usuario.objects.filter(id = id).first() 

            data  = request.data

            nombre = request.data['first_name']
            apellido = request.data['last_name']
            direccion = request.data['direccion']
            email = request.data['email']
            sexo = request.data['sexo']
            numCel = request.data['num_cel']
            documento = request.data['document_number']

            if isUsuario:
                usuarioSerializer = UsuarioSerializer(isUsuario , data = data , partial=True)
                 
                if usuarioSerializer.is_valid():
                    dni = isUsuario.document_number

                    if isUsuario.user_type.id in (2 , 3):
                        isCliente = Cliente.objects.filter(dni = dni)
                        isVeterinario = Veterinario.objects.filter(dni = dni)

                        if isCliente.exists():
                            isCliente.update(
                                dni = documento,
                                nombre = nombre,
                                apellido = apellido,
                                direccion = direccion,
                                num_cel = numCel,
                                correo = email,
                                sexo = sexo
                            )
                        
                        if isVeterinario.exists():
                            isVeterinario.update(
                                dni = dni,
                                nombre = nombre,
                                apellido = apellido,
                                direccion = direccion,
                                num_cel = numCel,
                                sexo = sexo,
                                correo = email
                            )
                    
                        usuarioSerializer.save()

                    isError = False
                    message = "Tu perfil fue actualizada con exito"
                else:
                    isError = True
                    message = f"error de lectura por lo siguiente: {usuarioSerializer.errors}"

                return Response({"is_error": isError, "message" : message} , status= status.HTTP_200_OK)
    except Exception as error:
        print(error)
        return Response({"is_error": True, "message" : error.message} , status= status.HTTP_200_OK)

@api_view(['PUT' , 'DELETE']) 
def UsuarioEliminacionFisicaLogica(request , pk = None):
    try:
        isUsuario = Usuario.objects.filter(id = pk)
        keyEvento = 0
        keyUsuario = request.data['key_usuario']

        if isUsuario.first():
            if request.method == 'PUT':
                keyEstado = request.data['key_estado']
                
                isUsuario.update(status_id=keyEstado)
                isError = False
                message = "Los datos fueron restaurado con exito" if keyEstado == 1 else "Los datos fueron anulado con exito"
                keyEvento = 6 if keyEstado == 1 else 3
            
            elif request.method == 'DELETE':
                isUsuario.delete()
                isError = False
                keyEvento = 4
                message = "Los datos fueron eliminados con exito"
            
            RegistrarHistorial(keyEvento, 'usuario', pk , keyUsuario , message)
        else:
            isError = True
            message = "Los datos a consultar no se encuentra registrado en nuestra base de datos"
        
        return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error) } , status= status.HTTP_200_OK)

#---------------------TIPO DE USUARIOS-----------------------
def ConsultarTipoUsuario():
    try:
        query = f"""
          SELECT
          id,
          tipo_usuario,
          descripcion,
          action
          FROM tipo_usuario
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}

@api_view(['GET'])
def ListarTipoUsuario(request):
    try:
        if request.method == 'GET':
            consulta = ConsultarTipoUsuario()
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return {'is_error': True , "message": str(error)}

#login - inicio de session
class ObtenerTokenLogin(TokenObtainPairView):
    serializer_class = AccesoTokenSerializer

#-------------------MEDICAMENTOS-------------------------
def ConsultarMedicamento():
    try:
        query = f"""
         SELECT 
         med.id,
         med.codigo,
         med.nombre,
         med.descripcion,
         es.id as key_estado,
         es.nombre as estado,
         es.color,
         es.icon
         FROM medicina med
         LEFT JOIN estado es on es.id = med.key_estado_id
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}

@api_view(['GET'])
def ListarMedicamento(request):
    try:
        if request.method == 'GET':
            consulta = ConsultarMedicamento()
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return {'is_error': True , "message": str(error)}

@api_view(['POST'])
def AgregarMedicamentos(request):
    try:
        if request.method == 'POST':
            isMedicamento = Medicina.objects.filter(nombre = request.data['nombre']) 

            if isMedicamento.count() == 0:
                medicamentoSerializer = MedicamentoSerializer(data = request.data)

                if medicamentoSerializer.is_valid(): 
                    medicamentoSerializer.save()

                    key = medicamentoSerializer.data['id']
                    isError = False
                    message = "Se registro con exito el medicamento"

                    Medicina.objects.filter(id=key).update(codigo = f'MED-00{key}')

                    descripcion = f"el medicamento por nombre {request.data['nombre']} fue registrado con exito"

                    RegistrarHistorial(1 , "medicina",key, request.data['key_usuario'], descripcion)
                else:
                    isError = True
                    message = f"error de lectura por lo siguiente: {str(medicamentoSerializer.errors)}"

            else:
                isError = True
                message = f"El medicamento {request.data['nombre']} ya se encuentra registrado"
            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK)

#-------------------Finalizacion de citas-------------------------
def ConsultarTriajeId(id):
    try:
        query = f"""
                select 
                * 
                from triaje
                where key_cita_id ={id}
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}

@api_view(['GET'])
def ListarTriaje(request , pk=None):
    try:
        if request.method == 'GET':
            consulta = ConsultarTriajeId(pk)
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return {'is_error': True , "message": str(error)}
    
def ConsultarRecetaId(id):
    try:
        query = f"""
                select 
                rc.id,
                rc.fecha_creacion,
                md.id as key_medicina,
                md.nombre as medicina,
                dr.tratamiento
                from receta rc
                LEFT JOIN detalle_receta dr on dr.key_receta_id = rc.id
                LEFT JOIN medicina md on md.id= dr.key_medicamento_id
                where key_cita_id ={id}
                """
        
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            resultado = ConvertirQueryADiccionarioDato(cursor)
            isError = False
            data = resultado
            message = "Consulta ejecutada con exito"

            return {'is_error': isError , 'data': data , "message": message}
    except Exception as error:
        isError = True
        data = []
        message = f"consulta sin exito debido al siguiente problema: {str(error)}"

        return {'is_error': isError , 'data': [] , "message": message}

@api_view(['GET'])
def ListarReceta(request , pk=None):
    try:
        if request.method == 'GET':
            consulta = ConsultarRecetaId(pk)
    
            return Response(consulta , status = status.HTTP_200_OK)
    except Exception as error:
        return {'is_error': True , "message": str(error)}

@api_view(['POST'])
def FinalizarCita(request): 
    try:
        if request.method == 'POST':

            isCita = Cita.objects.filter(id = request.data['key_cita'])

            isTriaje = Triaje.objects.filter(key_cita = request.data['key_cita'])

            isReceta = Receta.objects.filter(key_cita = request.data['key_cita'])

            if isCita.first():
                isCita.update(
                    motivo_consulta = request.data['motivo_consulta'],
                    observacion_sistema = request.data['observacion_sistema'],
                    diagnostico = request.data['diagnostico'],
                    recomendacion = request.data['recomendacion'],
                    key_estado_id = request.data['key_estado']
                )
                
                if isTriaje.count() == 0:
                    Triaje.objects.create(
                        key_cita_id = request.data['key_cita'],
                        peso = request.data['peso'],
                        temperatura = request.data['temperatura'],
                        frecuencia_cardica = request.data['frecuencia_cardica'],
                        frecuencia_respiratoria = request.data['frecuencia_respiratoria']
                    )
                else:
                    isTriaje.update(
                        peso = request.data['peso'],
                        temperatura = request.data['temperatura'],
                        frecuencia_cardica = request.data['frecuencia_cardica'],
                        frecuencia_respiratoria = request.data['frecuencia_respiratoria']
                    )
                    
                if isReceta.count() == 0:
                    createReceta = Receta.objects.create(
                        key_cita_id = request.data['key_cita'],
                    )
                    keyReceta = createReceta.id
                else:
                    keyReceta = isReceta.first().id

                for receta in request.data['receta']:
                    for keyMedicina in receta['id']:
                        Detalle_receta.objects.create(
                            key_medicamento_id = keyMedicina,
                            tratamiento = receta['tratamientos'],
                            key_receta_id = keyReceta
                        )
                    
                isError = False
                message = 'Los datos fueron guardados con exito, ademas se da por finalizada la cita.'
            else:
                isError = True
                message = 'Los datos de la cita no se encuentra'

            return Response({"is_error": isError, "message" : message} ,  status= status.HTTP_200_OK)
    except Exception as error:
        return Response({"is_error": True, "message" : str(error)} ,  status= status.HTTP_200_OK)

@api_view(['POST'])
def ReporteReceta(request):
    if request.method == 'POST':
        try:
            receta = ConsultarRecetaId(request.data['key_cita'])
            cita = ConsultarCitaId(request.data['key_cita'])
            data = []
            if receta['is_error'] == False and cita['is_error'] == False:
                if receta['data'][0]['key_medicina'] != None:
                    return FormatoReceta(cita['data'][0] ,receta['data'])
                
                return Response({'is_error' : True , 'message': 'no se encuentra la receta'} , status=status.HTTP_200_OK)
            else:
                return Response({'is_error' : True , 'message': 'no se encuentra la receta'} , status=status.HTTP_200_OK)
        except Exception as error:
            return Response({'is_error' : True , 'message': str(error)} , status=status.HTTP_200_OK)
        

def FormatoReceta(data , receta):
    try:
        #buffer = BytesIO()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="receta.pdf"'

        w, h = A4

        

        doc = SimpleDocTemplate(
            response,
            pagessize = A4,
            rightMargin=25,
            leftMargin=25, 
            topMargin=25, 
            bottomMargin=25
        )

        hoja = []
        
        logo = os.path.join(settings.BASE_DIR , 'media', 'logo.png')
        style = getSampleStyleSheet()

        style.add(
            ParagraphStyle(
                name='texto_cabecera',
                fontSize = 9,
                fontName='Helvetica-Bold'
            )
        )

        style.add(
            ParagraphStyle(
                name='texto_simple',
                fontSize = 9,
                fontName='Helvetica',
                textTransform='uppercase'
            )
        )

        style.add(
            ParagraphStyle(
                name='texto_cursive',
                fontSize = 9,
                fontName='Courier',
                alignment = 1,
            )
        )

        style.add(
            ParagraphStyle(
                name='salto_linea',
                spaceBefore=50, #TOP
                fontSize=8
            )
        )

        fechaReceta = str(receta[0]['fecha_creacion'])

        fecha = datetime.strptime(fechaReceta, '%Y-%m-%d %H:%M:%S.%f%z')

        # Formatear la fecha utilizando el filtro date de Django
        fechaFormateada = date(fecha, 'j \ M\. Y')


        encabezado  = [
                [Image(logo , width=2.5*cm , height=2.5*cm) , Paragraph(f"DRA. {data['nombre_completo_veterinario']}" , style= style['texto_cabecera'])  ,  Paragraph(fechaFormateada , style= style['texto_cabecera'])],
                ['' , Paragraph(f'{data["tipo_servicio"]}' , style= style['texto_cabecera']) , ''],
                ['' , Paragraph(f'Teléfono: {data["num_cel_vt"]}' , style= style['texto_cabecera']) , ''],
                ['' , Paragraph(f'Correo: {data["correo_vt"]}' , style= style['texto_cabecera']) , ''],
                ['' , Paragraph('Marcelino Champagnat Mz A, Sullana 20102' , style= style['texto_cabecera']) , ''],
                ['' , '' , '']
        ]

        boderEncabezado = Table(encabezado , colWidths=[(500 * 0.17) , (490 * 0.65) , (490 * 0.2)])
        boderEncabezado.setStyle(TableStyle([
            ('GRID',(0, 6), (-1, -1), .5,colors.grey),
            #('BOX', (0, 6), (-1, -1), 1,colors.grey),
            ('SPAN', (0, 0), (0, 5)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        informacionPaciente = [
            [Paragraph('Nombre' , style= style['texto_cabecera']) , Paragraph(f'{data["nombre_mascota"]}' , style= style['texto_simple'])],
            [Paragraph('Especie', style= style['texto_cabecera']) , Paragraph(f'{data["especie"]}' , style= style['texto_simple'])],
            [Paragraph('Raza', style= style['texto_cabecera']) , Paragraph(f'{data["nombre_raza"]}' , style= style['texto_simple'])],
            [Paragraph('Sexo', style= style['texto_cabecera']) , Paragraph(f'{data["sexo_mascota"]}' , style= style['texto_simple'])],
            [Paragraph('Edad', style= style['texto_cabecera']) , Paragraph(f'{data["edad"]}' , style= style['texto_simple'])],
            [Paragraph('Dueño', style= style['texto_cabecera']) , Paragraph(f'{data["nombre_completo_cliente"]}' , style= style['texto_simple'])],
        ]
        bordeInformacion = Table(informacionPaciente , colWidths=[(400*0.15) , (675*0.65)])
        bordeInformacion.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('GRID',(0, 6), (-1, -1), .5,colors.grey),
            ('BOTTOMPADDING', (0, 5), (-1, -1), 8),
            #('GRID',(0, 0), (-1, -1), .5,colors.grey),
        ]))

        datosAgrupados = {}
        datosReceta = []

        for items in receta:
            tratamientoActual = items['tratamiento']
            if tratamientoActual not in datosAgrupados:
                datosAgrupados[tratamientoActual] = []
            
            datosAgrupados[tratamientoActual].append(items['medicina'])
        
        for tratamiento, elementos in datosAgrupados.items():
            datosReceta.append({
                'tratamiento' : tratamiento,
                'medicamento' : elementos
            })

        medicinaAndIndicador = []
        for indicador in datosReceta:
            medicina = ', '.join(indicador['medicamento'])
            m = Paragraph(f"<b>{medicina}</b><br/> {indicador['tratamiento']}" , style= style['texto_simple'])
            medicinaAndIndicador.append([m])
         
        bordeMedicina = Table(medicinaAndIndicador , colWidths=[(770*0.65)])
        
        bordeMedicina.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 10)
        ]))

        firma = [
            [Paragraph(f"<i>{data['nombre_completo_veterinario']}</i>" , style = style['texto_cursive'])],
            ['FIRMA']
        ]

        tablaFirma = Table(firma, colWidths=[(400 * 0.45), (400*0.1), (400 *0.45)])
        tablaFirma.setStyle(TableStyle([
            ('GRID',(0,1),(-1,-2),0.5,colors.grey),
            #('SPAN', (0, 0), (0, 1)),
            # ('INNERGRID',(0,0),(0,1),0.5,colors.black),
            # ('LINEABOVE',(2,1),(2,1),0.5,colors.black), 
            ('ALIGN', (0, 0), (1, 2), 'CENTER'), 
            ('BOTTOMPADDING', (2, 0), (2, 0), 3),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))

        espacio = Paragraph('' , style= style['salto_linea'])
       
        hoja.append(boderEncabezado)
        hoja.append(bordeInformacion)
        hoja.append(bordeMedicina)
        hoja.append(espacio)
       
        hoja.append(tablaFirma)
        doc.build(hoja)

        return response
    except Exception as error:
        print(error)
        return {'is_error' : True , 'message' : f'no se genero con exito el documento por el siguiente problema: {str(error)}'}

@api_view(['POST'])
def ReporteHistorialClinico(request):
    if request.method == 'POST':
        try:
            receta = ConsultarRecetaId(request.data['key_cita'])
            cita = ConsultarCitaId(request.data['key_cita'])
            triaje = ConsultarTriajeId(request.data['key_cita'])
    
            if cita['is_error'] == False:
                return FormatoHistorialClinicaCita(cita['data'][0] ,receta['data'] , triaje['data'][0])
            else:
                return Response({'is_error' : True , 'message': 'no se encuentra el historial'} , status=status.HTTP_200_OK)
        except Exception as error:
            return Response({'is_error' : True , 'message': str(error)} , status=status.HTTP_200_OK)

def FormatoHistorialClinicaCita(data , receta , triaje):
    try:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="receta.pdf"'

        w, h = A4

        doc = SimpleDocTemplate(
            response,
            pagessize = A4,
            rightMargin=25,
            leftMargin=25, 
            topMargin=25, 
            bottomMargin=25
        )

        hoja = []
        
        logo = os.path.join(settings.BASE_DIR , 'media', 'logo.png')
        logoSecundario = os.path.join(settings.BASE_DIR , 'media', 'image (1).png')
        style = getSampleStyleSheet()

        style.add(
            ParagraphStyle(
                name='texto_cabecera',
                fontSize = 10,
                fontName='Helvetica-Bold',
                alignment = 1,
            )
        )

        style.add(
            ParagraphStyle(
                name='texto_simple',
                fontSize = 8,
                fontName='Helvetica',
                #textTransform='uppercase',
                alignment = 1,
            )
        )

        style.add(
            ParagraphStyle(
                name='texto_general',
                fontSize = 8,
                fontName='Helvetica',
                #textTransform='uppercase',
            )
        )

        style.add(
            ParagraphStyle(
                name='salto_linea',
                spaceBefore=20, #TOP
                fontSize=8
            )
        )

        encabezado = [
            [Image(logo , width=2.5*cm , height=2.5*cm) ,  Paragraph('Historial clínico'.upper() , style= style['texto_cabecera']) , Image(logoSecundario , width=3*cm , height=2.5*cm)],
            ['' ,  Paragraph('Clínica Veterinaria Champagnat' , style= style['texto_simple']) , ''],
            ['' ,  Paragraph('Central: 073-782656-994103307'  , style= style['texto_simple']) , ''],
            ['' ,  Paragraph('Av.Champagnat Mz A Lt 24, Sullana' , style= style['texto_simple']) , '']
        ]

        boderEncabezado = Table(encabezado , colWidths=[(500 * 0.17) , (490 * 0.65) , (490 * 0.2)])

        boderEncabezado.setStyle(TableStyle([
            ('GRID',(0, 4), (-1, -1), .5,colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), 
            #('BOX', (0, 6), (-1, -1), 1,colors.grey),
            ('SPAN', (0, 0), (0, 3)),
            ('SPAN', (2, -1), (2, -4)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        espacio = Paragraph('' , style= style['salto_linea'])

        fecha =  data['fecha_inicio']

        # Formatear la fecha utilizando el filtro date de Django
        fechaFormateada = date(fecha, 'j \ M\. Y')

        tablaDatosGenerales = [
            [Paragraph(f'<b>Fecha:</b> {fechaFormateada}'.upper() , style= style['texto_general']) , Paragraph(f'<b>Veterinario a cargo:</b> {data["nombre_completo_veterinario"]}'.upper() , style= style['texto_general']), ''],
            [Paragraph('<b>Datos del paciente</b>'.upper() , style= style['texto_general']) , '', ''],
            [Paragraph(f'<b>Nombre:</b> {data["nombre_mascota"]}'.upper() , style= style['texto_general']) , Paragraph(f'<b>Especie:</b> {data["especie"]}'.upper() , style= style['texto_general']), Paragraph(f'<b>Raza:</b> {data["nombre_raza"]}'.upper() , style= style['texto_general'])],
            [Paragraph(f'<b>edad:</b> {data["edad"]}'.upper() , style= style['texto_general']) , Paragraph(f'<b>Sexo:</b> {data["sexo_mascota"]}'.upper() , style= style['texto_general']),Paragraph('<b>COLOR:</b> ---' ,  style= style['texto_general'])],
        ]

        boderTablaGeneral =  Table(tablaDatosGenerales , colWidths=[(370 * 0.45) , (370 * 0.45) , (370 * 0.45)])
        boderTablaGeneral.setStyle(TableStyle([
            ('GRID',(0, 0), (-1, -1), .5,colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (1, 0), (-1, -4)),# +
            ('SPAN', (2, 1), (0, 1)),
        ]))

        tablaDatosCliente = [
            [Paragraph('<b>Datos del propietario</b>'.upper() , style= style['texto_general']) , '', ''],
            [Paragraph(f'<b>Nombre:</b> {data["nombre_completo_cliente"]}'.upper() , style= style['texto_general']) , Paragraph(f'<b>Nro. celular:</b> {data["num_cel"]}'.upper() , style= style['texto_general']), Paragraph(f'<b>Correo:</b> {data["correo"]}'.upper() , style= style['texto_general'])],
            [Paragraph(f'<b>Motivo Consulta</b> <br/> {data["motivo_consulta"]}'.upper() , style= style['texto_general']) , '', ''],
            
        ]

        boderTablaCliente =  Table(tablaDatosCliente , colWidths=[(370 * 0.45) , (370 * 0.45) , (370 * 0.45)])
        boderTablaCliente.setStyle(TableStyle([
            ('GRID',(0, 0), (-1, -1), .5,colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (0, 0), (-1, -3)),# +
            ('SPAN', (-1, -1), (-3, -1)),# +
        ]))

        tablaExamanen = [
            [Paragraph('<b>Examen Clínico</b>'.upper() , style= style['texto_general']) , '', '' ,''],
            [Paragraph('<b>Peso</b>'.upper() , style= style['texto_simple']) , Paragraph('<b>Temperatura</b>'.upper() , style= style['texto_simple']), Paragraph(f'<b>Frecuencia cardiaca</b>'.upper() , style= style['texto_simple']) , Paragraph(f'<b>Frecuencia respiratoria</b>'.upper() , style= style['texto_simple'])], 
            [Paragraph(triaje['peso'] , style= style['texto_simple']) , Paragraph(triaje['temperatura']  , style= style['texto_simple']), Paragraph(triaje['frecuencia_cardica'] , style= style['texto_simple']) , Paragraph(triaje['frecuencia_respiratoria']  , style= style['texto_simple'])]          
        ]

        boderTablaExamanen =  Table(tablaExamanen , colWidths=[(370 * 0.338) , (370 * 0.338) , (370 * 0.338) , (370 * 0.338)])   
        boderTablaExamanen.setStyle(TableStyle([
            ('GRID',(0, 0), (-1, -1), .5,colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (0, 0), (-1, -3)),# +
            # ('SPAN', (-1, -1), (-3, -1)),# +
        ]))

        tablaEstudio = [
            [Paragraph('<b>Estudio del caso</b>'.upper() , style= style['texto_general'])],
            [Paragraph(data['observacion_sistema'] if data['observacion_sistema'] != None else '', style= style['texto_general'])],
            [Paragraph('<b>DIAGNOSTICO</b>'.upper() , style= style['texto_general'])],
            [Paragraph(data['diagnostico']  if data['diagnostico'] != None  else '', style= style['texto_general'])],
        ]

        boderTablaEstudio =  Table(tablaEstudio , colWidths=[(800 * 0.627)])   
        boderTablaEstudio.setStyle(TableStyle([
            ('GRID',(0, 0), (-1, -1), .5,colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        tablaTratamiento = [
            [Paragraph('<b>PLAN DE TRATAMIENTO</b>'.upper() , style= style['texto_general'])],
        ]

        boderTablaTratamiento =  Table(tablaTratamiento , colWidths=[(800 * 0.627)])   
        boderTablaTratamiento.setStyle(TableStyle([
            ('GRID',(0, 0), (-1, -1), .5,colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        datosAgrupados = {}
        datosReceta = []

        for items in receta:
            tratamientoActual = items['tratamiento']
            if tratamientoActual not in datosAgrupados:
                datosAgrupados[tratamientoActual] = []
            
            datosAgrupados[tratamientoActual].append(items['medicina'])
        
        for tratamiento, elementos in datosAgrupados.items():
            datosReceta.append({
                'tratamiento' : tratamiento,
                'medicamento' : elementos
            })

        medicinaAndIndicador = []
        for indicador in datosReceta:
            if indicador['tratamiento'] != None and indicador['medicamento'][0] != None:
                medicina = ', '.join(indicador['medicamento'])
                m = Paragraph(f"<b>{medicina}</b><br/> {indicador['tratamiento']}" , style= style['texto_general'])
                medicinaAndIndicador.append([m])
            else:
                m = Paragraph("", style= style['texto_general'])
                medicinaAndIndicador.append([m])

        bordeMedicina = Table(medicinaAndIndicador , colWidths=[(800 * 0.627)])
        
        bordeMedicina.setStyle(TableStyle([
            ('GRID',(0, 0), (-1, -1), .5,colors.grey),
        ]))

        tablaRecomendacion = [
            [Paragraph('<b>Recomendaciones</b>'.upper() , style= style['texto_general'])],
            [Paragraph(data['recomendacion']  if data['recomendacion'] != None else '', style= style['texto_general'])],
        ]

        boderTablaRecomendacion =  Table(tablaRecomendacion , colWidths=[(800 * 0.627)])   
        boderTablaRecomendacion.setStyle(TableStyle([
            ('GRID',(0, 0), (-1, -1), .5,colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        tablaServicio = [
            [Paragraph('<b>Servicio</b>'.upper() , style= style['texto_general']) , '', '' ,''],
            [Paragraph('<b>Servicio general</b>'.upper() , style= style['texto_simple']) , Paragraph('<b>Tipo</b>'.upper() , style= style['texto_simple']), Paragraph(f'<b>Tipo de cita</b>'.upper() , style= style['texto_simple']) , Paragraph(f'<b>costo</b>'.upper() , style= style['texto_simple'])], 
            [Paragraph(data['nombre_servicio'] , style= style['texto_simple']) , Paragraph(data['tipo_servicio'].upper()   , style= style['texto_simple']), Paragraph(data['tipo_cita'].upper() , style= style['texto_simple']) , Paragraph(f"S/{str(data['precio'])}"  , style= style['texto_simple'])]          
        ]

        boderTablaServicio =  Table(tablaServicio , colWidths=[(370 * 0.338) , (370 * 0.338) , (370 * 0.338) , (370 * 0.338)])   
        boderTablaServicio.setStyle(TableStyle([
            ('GRID',(0, 0), (-1, -1), .5,colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (0, 0), (-1, -3)),# +
            # ('SPAN', (-1, -1), (-3, -1)),# +
        ]))

        hoja.append(boderEncabezado)
        hoja.append(espacio)
        hoja.append(boderTablaGeneral)
        hoja.append(boderTablaCliente)
        hoja.append(espacio)
        hoja.append(boderTablaExamanen)
        hoja.append(espacio)
        hoja.append(boderTablaEstudio)
        hoja.append(espacio)
        hoja.append(boderTablaTratamiento)
        hoja.append(bordeMedicina)
        hoja.append(espacio)
        hoja.append(boderTablaRecomendacion)
        hoja.append(espacio)
        hoja.append(boderTablaServicio)
        doc.build(hoja)

        return response
    except Exception as error:
        print(error)
        return {'is_error' : True , 'message' : f'no se genero con exito el documento por el siguiente problema: {str(error)}'}

@api_view(['POST'])
def ResetPassword(request):
    try:
        if request.method == 'POST':
            #ESTABLECEMOS CONEXION CON EL EMAIL
            asunto = 'Ya puedes restablecer tu contraseña 😇!'
            mensaje = 'Ya puedes restablecer tu contraseña 😇!'
            # destinatario = request.data['correo']
            nombreCampo = request.data['campo']
            valor = request.data['value']

            isUser = IsVerificarUser(nombreCampo , valor)
            isValidar = {
                'username': 'El Usuario no existe',
                'document_number': 'EL DNI no existe',	
                'email' : 'El correo electrónico no existe'
            }[nombreCampo]

            if(isUser['is_error'] == False and len(isUser['result']) != 0):
                destinatario = isUser['result'][0]['email']
                caracteres = string.ascii_letters + string.digits
                token = ''.join(secrets.choice(caracteres) for _ in range(32))
                link = "http://localhost:5173/reset-password/{0}".format(token)

                codigo = generarCodigo(6)
            
                contenidoHtml = render_to_string('reset-password.html', {'link': link , 'nombre_usuario':isUser['result'][0]['first_name'],  'current_year': datetime.now().strftime('%Y') , 'codigo' : codigo})
                
                statusCorreo = EnvioCorreo(asunto , mensaje , destinatario , contenidoHtml)

                dateAndTime = timezone.now()
                idUsuario = isUser['result'][0]['id']
                if statusCorreo['is_error'] == False:
                    #si hay un activo actualizar su estado y crear uno nuevo 
                    isVerificarActivo = RestablerUsuario.objects.filter(Q(key_usuario = idUsuario) and Q(is_activo = True))
                    
                    if isVerificarActivo.count() != 0:
                        isVerificarActivo.update(
                            is_activo = False
                        )
                    RestablerUsuario.objects.create(
                        key_usuario_id = idUsuario,
                        toke = token,
                        codigo_recuperacion = codigo,
                        expired = dateAndTime + timedelta(days=1) 
                    )
                    isError = False
                    message = 'Revise su Correo Electrónico y abra el enlace que le enviamos par continuar'
                else:
                    isError = True
                    message = 'ups.. Ocurrio un error'
            else:
                isError = True
                message = isValidar
                token = 0

            return Response({'is_error' : isError , 'message' : message , "token" : token} , status = status.HTTP_200_OK )
    except Exception as error:
       print(error)
       return Response({'is_error' : True , 'message' : error} , status = status.HTTP_200_OK)


def generarCodigo(logitud):
    usedCode = set()
    
    while True:
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits , k=logitud))
        
        if codigo not in usedCode:
            usedCode.add(codigo)
            return codigo
        
def EnvioCorreo(asunto , mensaje , destinatario , contenidoHtml):
    try:
        fromEmail = settings.EMAIL_HOST_USER

        with get_connection(
            host = settings.EMAIL_HOST,
            port = settings.EMAIL_PORT,
            username = settings.EMAIL_HOST_USER,
            password = settings.EMAIL_HOST_PASSWORD,
            use_tls = settings.EMAIL_USE_TLS,
        ) as connection:
            body = EmailMultiAlternatives(
                asunto,
                mensaje,
                fromEmail,
                [destinatario],
                connection= connection
            )

            body.attach_alternative(contenidoHtml , "text/html")

            if body.send():
                isError = False
                message = "Operacion exitosa"
            else:
                isError = True 
                message = 'operacion sin exito'

        return {'is_error': isError , 'message': message}
    except Exception as error:
        return {'is_error': True , 'message': error}