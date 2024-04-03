from django.urls import path
from app_veterinaria.api import *
from django.urls import path

urlpatterns = [
    #--------------------------HISTORIAL------------------------------------
    path('lista-log/' , ListaHistorial , name="lista_log"),

    #--------------------------API RENIEC------------------------------------
    path('consultar-dni/<str:dni>/' , ApiReniec , name="consultar_dni"),

    #--------------------------SERVICIOS------------------------------------
    path('lista-servicios/' , ListaServicios , name="lista_servicios"),
    path('agregar-servicios/' , AgregarServicios , name="agregar_servicios"),
    path('actualizar-servicios/<int:pk>/' , ActualizarServicio , name="actualizar_servicios"),
    path('recuperar-eliminar-servicios/<int:pk>/' , EliminacionFiscaLogica , name="recuperar_eliminar_servicios"),
    path('exportar-servicios/' , ExportarServicios , name="exportar_servicios"),
    path('total-servicios-utilizados/' , TotalServiciosUtilizados , name="total_servicios_utilizados"),
    
    #--------------------------TIPO DE SERVICIO------------------------------------
    path('lista-tipo-servicios/' , ListarTipoServicios , name="lista_tipo_servicios/"),
    path('agregar-tipo-servicios/' , AgregarTipoServicios , name="agregar_tipo_servicios"),
    path('actualizar-tipo-servicios/<int:pk>/' , ActualizarTipoServicio , name="actualizar_tipo_servicios"),
    path('recuperar-eliminar-tipo-servicios/<int:pk>/' , TipoServicioEliminacionFiscaLogica , name="recuperar_eliminar_tipo_servicios"),
    path('exportar-tipo-servicios/' , ExportarTipoServicios , name="exportar_tipo-servicios"),

    #--------------------------VETERINARIO------------------------------------
    path('lista-veterinarios/' , ListarVeterinarios , name="lista_veterinarios"),
    path('agregar-veterinarios/' , AgregarVeterinario , name="agregar_veterinarios"),
    path('actualizar-veterinarios/<int:pk>/' , ActualizarVeterinario , name="actualizar_veterinarios"),
    path('recuperar-eliminar-veterinarios/<int:pk>/' , VeterinarioEliminacionFiscaLogica , name="recuperar_eliminar_veterinarios"),
    path('exportar-veterinarios/' , ExportarVeterinario , name="exportar_veterinarios"),

    #--------------------------CLIENTES------------------------------------
    path('lista-clientes/' , ListarCientes , name="lista_clientes"),
    path('agregar-clientes/' , AgregarClientes , name="agregar_clientes"),
    path('actualizar-clientes/<int:pk>/' , ActualizarClientes , name="actualizar_cliente"),
    path('recuperar-eliminar-clientes/<int:pk>/' , ClienteEliminacionFiscaLogica , name="recuperar_eliminar_clientes"),
    path('exportar-clientes/' , ExportarCliente , name="exportar_clientes"),
    path('total-clientes-nuevo/' , TotalClientesNuevos , name="total_clientes"),
    path('total-clientes-frecuentes/' , ClientesFrecuentes , name="total_clientes_frecuentes"),

    #--------------------------RAZAS------------------------------------
    path('lista-razas/' , ListarRaza , name="lista_razas"),
    path('agregar-razas/' , AgregarRaza , name="agregar_razas"),
    path('actualizar-razas/<int:pk>/' , ActualizarRaza , name="actualizar_razas"),
    path('recuperar-eliminar-razas/<int:pk>/' , RazaEliminacionFiscaLogica , name="recuperar_eliminar_razas"),
    path('exportar-razas/' , ExportarRazas , name="exportar_razas"),

    #--------------------------TIPO DE MASCOTA------------------------------------
    path('lista-tipo-mascota/' , ListarTipoMascota, name="lista_tipo_mascota"),
    path('agregar-tipo-mascota/' , AgregarTipoMascota , name="agregar_tipo_mascota"),
    path('actualizar-tipo-mascota/<int:pk>/' , ActualizarTipoMascota , name="actualizar_tipo_mascota"),
    path('recuperar-eliminar-tipo-mascota/<int:pk>/' , TipoMascotaEliminacionFiscaLogica , name="recuperar_eliminar_tipo-mascota"),
    path('exportar-tipo-mascota/' , ExportarTipoMascota , name="exportar_tipo_mascota"),

    #-------------------------- MASCOTA ------------------------------------
    path('lista-mascota/' , ListarMacotas , name="lista_mascota"),
    path('agregar-mascota/' , AgregarMascota , name="agregar_mascota"),
    path('actualizar-mascota/<int:pk>/' , ActualizarMascota , name="actualizar_mascota"),
    path('recuperar-eliminar-mascota/<int:pk>/' , MascotaEliminacionFiscaLogica , name="recuperar_eliminar_mascota"),
    path('exportar-mascota/' , ExportarMascota , name="exportar_mascota"),
    path('total-mascotas-clientes/' , TotalMascotasClientes , name="total_mascotas_cliente"),

    #-------------------------- TIPO DE CITA ------------------------------------
    path('lista-tipo-citas/' , ListarTipoCita , name="lista_tipo_citas"),

    #-------------------------- CITA ------------------------------------
    path('lista-citas-id/<int:pk>/' , ListarCitaId , name="lista_citas_id"),
    path('lista-citas/' , ListarCita , name="lista_citas"),
    path('agregar-citas/' , AgregarCita , name="agregar_cita"),
    path('actualizar-citas/<int:pk>/' , ActualizarCita , name="actualizar_citas"),
    path('recuperar-eliminar-citas/<int:pk>/' , CitaEliminacionFiscaLogica , name='recuperar_eliminar_citas'),
    path('reprograr-citas/<int:pk>/' , ReprogramarCita , name='reprograr_cita'),
    path('finalizar-citas/' , FinalizarCita , name='finalizar_citas'),
    path('total-citas-estados/' , TotalCitasEstados , name='total_citas_estados'),
    path('total-citas-ingresos/' , TotalIngresosCitas , name='total_citas_estados'),

    #-------------------------- PREGUNTAS FRECUENTES ------------------------------------
    path('lista-preguntas-frecuentes/' , ListarPreguntaFrecuntes , name="lista_preguntas_frecuentes"),
    path('agregar-preguntas-frecuentes/' , AgregarPreguntaFrecuntes , name="agregar_preguntas_frecuentes"),
    path('actualizar-preguntas-frecuentes/<int:pk>/' , ActualizarPreguntasFrecuentes , name="actualizar_preguntas_frecuentes"),
    path('recuperar-eliminar-preguntas-frecuentes/<int:pk>/' , PreguntasFrecuentesEliminacionFiscaLogica , name="recuperar_eliminar_preguntas_frecuentes"),
    path('exportar-preguntas-frecuentes/' , ExportarPreguntasFrecuentes , name="exportar_preguntas_frecuentes"),

    #-------------------------- USUARIOS ------------------------------------
    path('lista-usuario/' , ListarUsuario , name="lista_usuario"),
    path('agregar-usuario/' , AgregarUsuario , name="agregar_usuario"),
    path('actualizar-usuario/<int:pk>/' , ActualizarUsuario , name="actualizar_usuario"),
    path('recuperar-eliminar-usuario/<int:pk>/' , UsuarioEliminacionFisicaLogica , name="recuperar_eliminar_usuario"),

    #--------------------------'TIPOS DE USUARIOS ------------------------------------
    path('lista-tipo-usuario/' , ListarTipoUsuario , name="lista_tipo-usuario"),

    #--------------------------'OBTENER TOKEN LOGIN ------------------------------------
    path('obtener-token/' , ObtenerTokenLogin.as_view()),

    #--------------------------MEDICAMENTO------------------------------------
    path('lista-medicamento/' , ListarMedicamento , name="lista_medicamento"),
    path('agregar-medicamento/' , AgregarMedicamentos , name="agregar_medicamento"),

    #--------------------------RECETA------------------------------------
    path('lista-receta/<int:pk>/' , ListarReceta , name="lista_receta"),
    path('reporte-receta/' , ReporteReceta , name="reporte_receta"),

    #--------------------------TRIAJE------------------------------------
    path('lista-triaje/<int:pk>/' , ListarTriaje , name="lista_triaje"),

    #------------------------HISTORIAL CLINICO--------------------------------
    path('reporte-historial-clinico/' , ReporteHistorialClinico , name="reporte_historial_clinico"),

]