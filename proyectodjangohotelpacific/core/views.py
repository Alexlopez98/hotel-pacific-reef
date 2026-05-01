from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps
# Importamos el Perfil recién creado
from .models import Habitacion, Reserva, Pago, Perfil
from .forms import HabitacionForm
from datetime import timedelta, datetime
import json


# --- DECORADOR ---
def redirect_if_authenticated(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('habitaciones')
        return view_func(request, *args, **kwargs)
    return wrapper

# --- VISTAS PÚBLICAS ---
@redirect_if_authenticated
def index_view(request):
    return render(request, 'index.html')

def rooms_view(request):
    lista_habitaciones = Habitacion.objects.all()
    return render(request, 'rooms.html', {
        'habitaciones': lista_habitaciones
    })


@redirect_if_authenticated
def register_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_completo')
        rut_cuerpo = request.POST.get('rut_cuerpo')
        rut_dv = request.POST.get('rut_dv')
        email = request.POST.get('email')
        password = request.POST.get('password')

        rut_completo = f"{rut_cuerpo}-{rut_dv}"

        # 1. Validar correo en Django
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este correo ya está registrado.')
            return redirect('registro')

        # 2. Validar RUT en tu tabla Perfil
        if Perfil.objects.filter(rut=rut_completo).exists():
            messages.error(request, 'Este RUT ya está registrado.')
            return redirect('registro')

        # 3. Crear usuario base
        user = User.objects.create_user(
            username=email, # Usamos el email como username para facilitar el login
            email=email,
            password=password
        )
        user.first_name = nombre
        user.save()

        # 4. Crear Perfil extendido en Oracle
        Perfil.objects.create(
            usuario=user,
            rut=rut_completo,
            rol='Turista'
        )

        login(request, user)
        return redirect('habitaciones')

    return render(request, 'register.html')


@redirect_if_authenticated
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Como en el registro pusimos el email en username, autenticamos directamente
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('habitaciones')
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')
            return redirect('login')

    return render(request, 'login.html')


def room_detail(request, hab_id):
    habitacion = get_object_or_404(Habitacion, id_habitacion=hab_id)

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

    return render(request, 'roomdetail.html', {
        'hab': habitacion,
        'fechas_bloqueadas': json.dumps(fechas_bloqueadas)
    })


# --- RESERVA ---
@login_required
def crear_reserva_provisional(request, id_habitacion):
    if request.method == 'POST':
        hab = get_object_or_404(Habitacion, id_habitacion=id_habitacion)

        f_ingreso_str = request.POST.get('fecha_ingreso')
        f_salida_str = request.POST.get('fecha_salida')
        total_str = request.POST.get('total_estimado')

        if not f_ingreso_str or not f_salida_str:
            messages.error(request, "⚠️ Selecciona fechas válidas.")
            return redirect('roomdetail', hab_id=id_habitacion)

        f_ingreso = datetime.strptime(f_ingreso_str, "%Y-%m-%d").date()
        f_salida = datetime.strptime(f_salida_str, "%Y-%m-%d").date()

        if f_salida <= f_ingreso:
            messages.error(request, "La fecha de salida debe ser mayor a la de ingreso.")
            return redirect('roomdetail', hab_id=id_habitacion)

        existe_choque = Reserva.objects.filter(
            habitacion=hab,
            estado_reserva__in=['Confirmada', 'Pendiente'],
            fecha_ingreso__lt=f_salida,
            fecha_salida__gt=f_ingreso
        ).exists()

        if existe_choque:
            messages.warning(request, "Fechas no disponibles.")
            return redirect('roomdetail', hab_id=id_habitacion)

        try:
            total = int(total_str)

            reserva_nueva = Reserva.objects.create(
                id_usuario=request.user.id,
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

        except Exception:
            messages.error(request, "Error al crear la reserva.")
            return redirect('roomdetail', hab_id=id_habitacion)

    return redirect('habitaciones')


@login_required
def confirmar_pago_final(request, id_reserva):
    if request.method == 'POST':
        reserva = get_object_or_404(Reserva, id_reserva=id_reserva)
        reserva.estado_reserva = 'Confirmada'
        reserva.save()

        messages.success(request, f"Reserva #{reserva.id_reserva} confirmada.")
        return redirect('habitaciones')

    return redirect('habitaciones')


# --- PERFIL DEL USUARIO ---
@login_required(login_url='login')
def perfil_usuario(request):
    # Traemos el perfil usando el usuario de la sesión
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        # Procesamos la subida de imagen a S3
        if 'foto_perfil' in request.FILES:
            perfil.foto_perfil = request.FILES['foto_perfil']
            perfil.save()
            messages.success(request, '¡Foto de perfil actualizada correctamente!')
            return redirect('perfil_usuario')

    return render(request, 'user.html', {'perfil': perfil})


# --- ADMIN ---
@login_required
def agregar_habitacion(request):
    if request.method == 'POST':
        form = HabitacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habitación añadida.')
            return redirect('habitaciones')
    else:
        form = HabitacionForm()

    return render(request, 'form_habitacion.html', {
        'form': form,
        'titulo': 'Nueva Habitación'
    })


@login_required
def editar_habitacion(request, id):
    habitacion = get_object_or_404(Habitacion, id_habitacion=id)

    if request.method == 'POST':
        form = HabitacionForm(request.POST, instance=habitacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habitación actualizada.')
            return redirect('habitaciones')
    else:
        form = HabitacionForm(instance=habitacion)

    return render(request, 'form_habitacion.html', {
        'form': form,
        'titulo': 'Editar Habitación'
    })