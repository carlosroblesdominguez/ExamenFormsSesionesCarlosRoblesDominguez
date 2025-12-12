from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.db.models import Prefetch, Count, Max, Q
from django.contrib import messages
from .models import *
from .forms import *
from datetime import datetime, date, time
from django.contrib.auth import login
from django.contrib.auth.decorators import permission_required

# Create your views here.
def index(request):
    if(not "fecha_inicio" in request.session):
        request.session["fecha_inicio"]=datetime.now().strftime('%d/%m/%Y %H:%M')
    return render(request, 'examen_forms_sesiones/index.html')

# ----------------
# Autenticacion 
# ----------------

# django.core.exceptions.FieldError: Unknown field(s) (edad) specified for Usuario

def registrar_usuario(request):
    if request.method=='POST':
        formularioRegistro = RegistroForm(request.POST)
        if formularioRegistro.is_valid():
            user=formularioRegistro.save()
            rol=int(formularioRegistro.cleaned_data.get('rol'))
            
            # perfil de paciente con los campos obligatorios
            if(rol==Usuario().PACIENTE):
                # Asignar paciente a grupo Pacientes ya existente
                user.groups.add(Group.objects.get(name='Pacientes'))
                
                paciente=Paciente.objects.create(usuario=user)
                
                paciente.save()
            elif(rol==Usuario().INVESTIGADOR):
                # Asignar investigador a grupo Investigadores ya existente
                user.groups.add(Group.objects.get(name='Investigadores'))
                
                investigador=Investigador.objects.create(usuario=user)
                investigador.save()
            return redirect('login')
    else:
        formularioRegistro=RegistroForm()
    return render(request, 'registration/signup.html',{'formularioRegistro':formularioRegistro})

# ----------------------------
# Crear Ensayo Clínico
# ----------------------------
def ensayoclinico_create_valid(formulario):
    """
    Valida y guarda el formulario de ensayo clínico.
    Devuelve True si se guardó correctamente, False si hubo error.
    """
    ensayoclinico_creado = False
    if formulario.is_valid():
        try:
            formulario.save()
            ensayoclinico_creado = True
        except Exception as e:
            # Mostrar el error en consola
            print("Error al guardar ensayo clínico: ", e)
    else:
        # Mostrar errores de validación
        print("Formulario no válido: ", formulario.errors)
    return ensayoclinico_creado
@permission_required('examen_forms_sesiones.add_ensayoclinico')
def ensayoclinico_create(request):
    """
    Vista para crear un nuevo ensayo clínico.
    - Si es GET: muestra el formulario vacío.
    - Si es POST: valida y guarda los datos del formulario.
    """
    datosFormulario = None
    if request.method == "POST":
        datosFormulario = request.POST

    # Creamos el formulario (vacío o con datos)
    formulario = EnsayoClinicoModelForm(datosFormulario)

    # Si es POST intentamos guardar el ensayo clínico
    if request.method == "POST":
        ensayoclinico_creado = ensayoclinico_create_valid(formulario)
        if ensayoclinico_creado:
            nombre = formulario.cleaned_data.get('nombre')
            # Mensaje de éxito
            messages.success(request, f"El ensayo clínico '{nombre}' se ha creado correctamente")
            # Redirigimos a la lista de ensayos clínicos
            return redirect('lista_ensayos_clinicos')

    # Renderizamos el formulario
    return render(request, 'examen_forms_sesiones/ensayos_clinicos/ensayoclinico_create.html', {"formulario": formulario})

# ----------------------------
# Leer / Buscar Ensayos Clínicos
# ----------------------------
'''
Búsqueda avanzada con los siguientes filtros:
Restricción por usuario logueado:

Investigador: solo ve los ensayos que haya creado,
Paciente: solo ve ensayos en los que está incluido
'''
@permission_required('examen_forms_sesiones.view_ensayoclinico')
def ensayoclinico_buscar(request):
    """
    Vista para buscar y listar ensayos clínicos.
    Muestra un formulario de búsqueda y los resultados filtrados.
    """
    # Obtener todos los ensayos clínicos inicialmente
    ensayos_clinicos = EnsayoClinico.objects.all()

    # Procesar el formulario de búsqueda
    formulario = EnsayoClinicoBusquedaForm(request.GET or None)
    if formulario.is_valid():
        nombre = formulario.cleaned_data.get('nombre')
        fecha_fin_desde = formulario.cleaned_data.get('fecha_fin_desde')
        fecha_fin_hasta = formulario.cleaned_data.get('fecha_fin_hasta')
        nivel_seguimiento = formulario.cleaned_data.get('nivel_seguimiento')
        pacientes = formulario.cleaned_data.get('pacientes')

        # Aplicar filtros según los datos del formulario
        if nombre:
            ensayos_clinicos = ensayos_clinicos.filter(
                Q(nombre__icontains=nombre) | Q(descripcion__icontains=nombre)
            )
        if fecha_fin_desde:
            ensayos_clinicos = ensayos_clinicos.filter(fecha_fin__gte=fecha_fin_desde)
        if fecha_fin_hasta:
            ensayos_clinicos = ensayos_clinicos.filter(fecha_fin__lte=fecha_fin_hasta)
        if nivel_seguimiento is not None:
            ensayos_clinicos = ensayos_clinicos.filter(nivel_seguimiento__gte=nivel_seguimiento)
        if pacientes:
            for paciente in pacientes:
                ensayos_clinicos = ensayos_clinicos.filter(pacientes=paciente)

    # Renderizar la plantilla con el formulario y los resultados
    return render(request, 'examen_forms_sesiones/ensayos_clinicos/ensayoclinico_buscar.html', {
        "formulario": formulario,
        "ensayos_clinicos": ensayos_clinicos
    })
    
# ----------------------------
# Editar Ensayo Clínico
# ----------------------------
@permission_required('examen_forms_sesiones.change_ensayoclinico')
def ensayoclinico_editar(request, ensayoclinico_id):
    """
    Vista para editar un ensayo clínico existente
    """
    # Obtener el ensayo clínico a editar
    ensayoclinico = EnsayoClinico.objects.get(id=ensayoclinico_id)
    datosFormulario = None

    if request.method == "POST":
        datosFormulario = request.POST

    # Creamos el formulario con la instancia del ensayo clínico
    formulario = EnsayoClinicoModelForm(datosFormulario, instance=ensayoclinico)

    if request.method == "POST":
        if formulario.is_valid():
            try:
                formulario.save()
                nombre = formulario.cleaned_data.get('nombre')
                messages.success(request, f"La promoción '{nombre}' se ha modificado correctamente")
                return redirect('lista_ensayos_clinicos')
            except Exception as e:
                print("Error al editar promoción:", e)

    # Renderizamos formulario de edición
    return render(request, 'examen_forms_sesiones/ensayos_clinicos/ensayoclinico_editar.html', {
        "formulario": formulario,
        "ensayoclinico": ensayoclinico
    })

# ----------------------------
# Eliminar Ensayo Clínico
# ----------------------------
@permission_required('examen_forms_sesiones.delete_ensayoclinico')
def ensayoclinico_eliminar(request, ensayoclinico_id):
    """
    Vista para eliminar un ensayo clínico existente
    """
    # Obtener el ensayo clínico a eliminar
    ensayoclinico = EnsayoClinico.objects.get(id=ensayoclinico_id)

    if request.method == "POST":
        nombre = ensayoclinico.nombre
        try:
            ensayoclinico.delete()
            messages.success(request, f"El ensayo clínico '{nombre}' se ha eliminado correctamente")
            return redirect('lista_ensayos_clinicos')
        except Exception as e:
            print("Error al eliminar ensayo clínico:", e)

    # Renderizamos confirmación de eliminación
    return render(request, 'examen_forms_sesiones/ensayos_clinicos/ensayoclinico_eliminar.html', {
        "ensayoclinico": ensayoclinico
    })