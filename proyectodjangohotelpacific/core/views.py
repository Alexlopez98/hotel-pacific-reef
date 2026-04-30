from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from .models import Habitacion, Reserva
from .forms import HabitacionForm
from datetime import timedelta
import json

# --- VISTAS PÚBLICAS ---

def index_view(request):
    return render(request, 'index.html')

def rooms_view(request):
    lista_habitaciones = Habitacion.objects.all()
    return render(request, 'rooms.html', {
        'habitaciones': lista_habitaciones
    })

def register_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_completo')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este correo ya está registrado.')
            return redirect('registro') 
            
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = nombre
        user.save()
        
        login(request, user)
        return redirect('habitaciones')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('habitaciones')
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')
            return redirect('login')
    return render(request, 'login.html')

def room_detail(request, hab_id):
    # Asegúrate que el campo en tu modelo sea id_habitacion
    habitacion = get_object_or_404(Habitacion, id_habitacion=hab_id)
    
    # Buscamos las reservas activas para bloquear fechas en el calendario
    reservas = Reserva.objects.filter(
        habitacion=habitacion, 
        estado_reserva__in=['Confirmada', 'Pendiente']
    )
    
    fechas_bloqueadas = []
    for r in reservas:
        actual = r.fecha_ingreso
        while actual <= r.fecha_salida:
            fechas_bloqueadas.append(actual.strftime('%Y-%m-%d'))
            actual += timedelta(days=1)
            
    context = {
        'hab': habitacion,
        'fechas_bloqueadas': json.dumps(fechas_bloqueadas)
    }
    return render(request, 'roomdetail.html', context)

# --- FLUJO DE RESERVA Y PAGO ---

def crear_reserva_provisional(request, id_habitacion):
    if request.method == 'POST':
        hab = get_object_or_404(Habitacion, id_habitacion=id_habitacion)
        
        # Obtener datos del POST (Nombres exactos del HTML)
        f_ingreso = request.POST.get('fecha_ingreso')
        f_salida = request.POST.get('fecha_salida')
        total_str = request.POST.get('total_estimado')

        # VALIDACIÓN 1: Fechas vacías
        if not f_ingreso or not f_salida:
            messages.error(request, "⚠️ Por favor, selecciona las fechas en el calendario.")
            return redirect('roomdetail', hab_id=id_habitacion)

        # VALIDACIÓN 2: Anticolisión (No pisar otras reservas)
        existe_choque = Reserva.objects.filter(
            habitacion=hab,
            estado_reserva__in=['Confirmada', 'Pendiente'],
            fecha_ingreso__lt=f_salida,
            fecha_salida__gt=f_ingreso
        ).exists()

        if existe_choque:
            messages.warning(request, "¡Lo sentimos! Alguna de las fechas seleccionadas ya no está disponible. 😊")
            return redirect('roomdetail', hab_id=id_habitacion)

        # CREACIÓN DE LA RESERVA ÚNICA (Estado Pendiente)
        try:
            total = int(total_str)
            reserva_nueva = Reserva.objects.create(
                id_usuario=request.user.id if request.user.is_authenticated else None,
                habitacion=hab,
                fecha_ingreso=f_ingreso,
                fecha_salida=f_salida,
                total_estimado=total,
                estado_reserva='Pendiente'
            )
            
            pago_parcial = int(total * 0.3)

            return render(request, 'pago.html', {
                'hab': hab,
                'reserva': reserva_nueva,
                'ingreso': f_ingreso,
                'salida': f_salida,
                'total': total,
                'parcial': pago_parcial,
            })
        except Exception as e:
            messages.error(request, "Error al procesar la reserva. Inténtalo de nuevo.")
            return redirect('roomdetail', hab_id=id_habitacion)

    return redirect('habitaciones')

@login_required
def confirmar_pago_final(request, id_reserva):
    """
    ESTO EDITA LA RESERVA, NO CREA OTRA.
    """
    if request.method == 'POST':
        # Buscamos la reserva pendiente por su ID
        reserva = get_object_or_404(Reserva, id_reserva=id_reserva)
        
        # Cambiamos el estado de la reserva existente
        reserva.estado_reserva = 'Confirmada'
        reserva.save() # Aquí se guarda el cambio en la misma fila de la BD
        
        messages.success(request, f"¡Reserva #{reserva.id_reserva} confirmada! Te esperamos.")
        return redirect('habitaciones')
    
    return redirect('habitaciones')

# --- VISTAS DE ADMINISTRACIÓN (CRUD) ---

@login_required
def agregar_habitacion(request):
    if request.method == 'POST':
        form = HabitacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habitación añadida con éxito.')
            return redirect('habitaciones')
    else:
        form = HabitacionForm()
    return render(request, 'form_habitacion.html', {'form': form, 'titulo': 'Nueva Habitación'})

@login_required
def editar_habitacion(request, id):
    habitacion = get_object_or_404(Habitacion, id_habitacion=id)
    if request.method == 'POST':
        form = HabitacionForm(request.POST, instance=habitacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habitación actualizada correctamente.')
            return redirect('habitaciones')
    else:
        form = HabitacionForm(instance=habitacion)
    return render(request, 'form_habitacion.html', {'form': form, 'titulo': 'Editar Habitación'})