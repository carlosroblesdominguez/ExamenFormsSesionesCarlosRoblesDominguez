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
def registrar_usuario(request):
    if request.method=='POST':
        formularioRegistro = RegistroForm(request.POST)
        if formularioRegistro.is_valid():
            user=formularioRegistro.save()
            rol=int(formularioRegistro.cleaned_data.get('rol'))
            
            if(rol==Usuario().CLIENTE):
                cliente=Cliente.objects.create(usuario=user)
                cliente.save()
            elif(rol==Usuario().STAFF):
                cliente=Staff.objects.create(usuario=user)
                cliente.save()
            return redirect('login')
    else:
        formularioRegistro=RegistroForm()
    return render(request, 'registration/signup.html',{'formularioRegistro':formularioRegistro})

# ----------------------------
# Crear Promocion
# ----------------------------
def promocion_create_valid(formulario):
    """
    Valida y guarda el formulario de promoción.
    Devuelve True si se guardó correctamente, False si hubo error.
    """
    promocion_creada = False
    if formulario.is_valid():
        try:
            formulario.save()
            promocion_creada = True
        except Exception as e:
            # Mostrar el error en consola
            print("Error al guardar promocion: ", e)
    else:
        # Mostrar errores de validación
        print("Formulario no válido: ", formulario.errors)
    return promocion_creada

@permission_required('examen_forms_sesiones.add_promocion')
def promocion_create(request):
    """
    Vista para crear una nueva promoción.
    - Si es GET: muestra el formulario vacío.
    - Si es POST: valida y guarda los datos del formulario.
    """
    datosFormulario = None
    if request.method == "POST":
        datosFormulario = request.POST

    # Creamos el formulario (vacío o con datos)
    formulario = PromocionModelForm(datosFormulario)

    # Si es POST intentamos guardar la promoción
    if request.method == "POST":
        promocion_creada = promocion_create_valid(formulario)
        if promocion_creada:
            nombre = formulario.cleaned_data.get('nombre')
            # Mensaje de éxito
            messages.success(request, f"La promoción '{nombre}' se ha creado correctamente")
            # Redirigimos a la lista de promociones
            return redirect('lista_promociones')

    # Renderizamos el formulario
    return render(request, 'examen_forms_sesiones/promociones/promocion_create.html', {"formulario": formulario})

# ----------------------------
# Leer / Buscar Promociones
# ----------------------------
@permission_required('examen_forms_sesiones.view_promocion')
def promocion_buscar(request):
    """
    Vista para buscar/listar promociones con filtros avanzados:
    - Texto en nombre/descripcion
    - Fecha fin desde/hasta
    - Descuento mínimo
    - Selección de usuarios
    - Promociones activas
    """
    mensaje_busqueda = ""
    promociones = Promocion.objects.none()  # Por defecto lista vacía
    formulario = PromocionModelForm(request.GET or None)

    if len(request.GET) > 0 and formulario.is_valid():
        # Extraemos los datos del formulario
        nombre_desc = formulario.cleaned_data.get('nombre')
        fecha_fin_desde = request.GET.get('fecha_fin_desde', None)
        fecha_fin_hasta = request.GET.get('fecha_fin_hasta', None)
        descuento_min = formulario.cleaned_data.get('descuento')
        usuarios = formulario.cleaned_data.get('usuarios')
        esta_activa = formulario.cleaned_data.get('esta_activa')

        filtros_aplicados = []
        filtros = Q()  # Objeto Q para filtros dinámicos

        # Filtrar por texto en nombre o descripción
        if nombre_desc:
            filtros &= Q(nombre__icontains=nombre_desc) | Q(descripcion__icontains=nombre_desc)
            filtros_aplicados.append(f"Texto: '{nombre_desc}'")
        # Filtrar por fecha fin desde
        if fecha_fin_desde:
            filtros &= Q(fecha_fin__gte=fecha_fin_desde)
            filtros_aplicados.append(f"Fecha fin desde: '{fecha_fin_desde}'")
        # Filtrar por fecha fin hasta
        if fecha_fin_hasta:
            filtros &= Q(fecha_fin__lte=fecha_fin_hasta)
            filtros_aplicados.append(f"Fecha fin hasta: '{fecha_fin_hasta}'")
        # Filtrar por descuento mínimo
        if descuento_min is not None:
            filtros &= Q(descuento__gte=descuento_min)
            filtros_aplicados.append(f"Descuento ≥ {descuento_min}")
        # Filtrar por usuarios seleccionados
        if usuarios:
            filtros &= Q(usuarios__in=usuarios)
            filtros_aplicados.append(f"Usuarios seleccionados")
        # Filtrar por promociones activas
        if esta_activa is not None:
            filtros &= Q(esta_activa=esta_activa)
            filtros_aplicados.append(f"Activa: {esta_activa}")

        # Aplicamos los filtros y eliminamos duplicados (many-to-many)
        promociones = Promocion.objects.filter(filtros).distinct()
        mensaje_busqueda = " | ".join(filtros_aplicados)

        # Renderizamos resultados filtrados
        return render(request, 'examen_forms_sesiones/promociones/promocion_buscar.html', {
            "formulario": formulario,
            "promociones": promociones,
            "texto_busqueda": mensaje_busqueda
        })

    # Si no hay GET, mostramos la búsqueda vacía
    return render(request, 'examen_forms_sesiones/promociones/promocion_buscar.html', {
        "formulario": formulario,
        "promociones": promociones
    })

# ----------------------------
# Editar Promocion
# ----------------------------
@permission_required('examen_forms_sesiones.change_promocion')
def promocion_editar(request, promocion_id):
    """
    Vista para editar una promoción existente
    """
    # Obtener la promoción a editar
    promocion = Promocion.objects.get(id=promocion_id)
    datosFormulario = None

    if request.method == "POST":
        datosFormulario = request.POST

    # Creamos el formulario con la instancia de la promoción
    formulario = PromocionModelForm(datosFormulario, instance=promocion)

    if request.method == "POST":
        if formulario.is_valid():
            try:
                formulario.save()
                nombre = formulario.cleaned_data.get('nombre')
                messages.success(request, f"La promoción '{nombre}' se ha modificado correctamente")
                return redirect('lista_promociones')
            except Exception as e:
                print("Error al editar promoción:", e)

    # Renderizamos formulario de edición
    return render(request, 'examen_forms_sesiones/promociones/promocion_editar.html', {
        "formulario": formulario,
        "promocion": promocion
    })

# ----------------------------
# Eliminar Promocion
# ----------------------------
@permission_required('examen_forms_sesiones.delete_promocion')
def promocion_eliminar(request, promocion_id):
    """
    Vista para eliminar una promoción
    """
    promocion = Promocion.objects.get(id=promocion_id)
    try:
        promocion.delete()
        messages.success(request, f"La promoción '{promocion.nombre}' ha sido eliminada")
    except Exception as e:
        print("Error al eliminar promoción:", e)
    # Redirigimos a la lista
    return redirect('lista_promociones')