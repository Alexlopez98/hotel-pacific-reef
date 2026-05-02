from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps
from .models import Habitacion, Reserva, Pago, Perfil
from .forms import HabitacionForm
from datetime import timedelta, datetime
from django.utils import timezone
import json
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
# =========================
# LÓGICA DE CANCELACIÓN (Añadida)
# =========================
def cancelar_reservas_expiradas():
    # 1. Definimos el tiempo límite (10 segundos atrás)
    limite = timezone.now() - timedelta(seconds=10)
    
    # PASO A: Las que llevan > 10 seg pendientes, pasan a 'Cancelada'
    # (Esto las marca para ser eliminadas en el siguiente ciclo o simplemente para avisar)
    Reserva.objects.filter(
        estado_reserva='Pendiente',
        fecha_creacion__lt=limite
    ).update(estado_reserva='Cancelada')
    
    # PASO B: Las que ya están como 'Cancelada' se eliminan de la base de datos
    # Así limpiamos lo que el sistema ya descartó antes
    eliminadas, _ = Reserva.objects.filter(estado_reserva='Cancelada').delete()
    
    if eliminadas > 0:
        print(f"DEBUG: Cinta transportadora activa. Se eliminaron {eliminadas} registros obsoletos.")

# =========================
# DECORADOR
# =========================
def redirect_if_authenticated(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('habitaciones')
        return view_func(request, *args, **kwargs)
    return wrapper

# =========================
# PUBLICAS
# =========================
@redirect_if_authenticated
def index_view(request):
    return render(request, 'index.html')

def rooms_view(request):
    cancelar_reservas_expiradas()  # 👈 Se limpia al cargar la lista
    lista_habitaciones = Habitacion.objects.all()
    return render(request, 'rooms.html', {
        'habitaciones': lista_habitaciones
    })

# =========================
# REGISTRO
# =========================
@redirect_if_authenticated
def register_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_completo')
        rut_cuerpo = request.POST.get('rut_cuerpo')
        rut_dv = request.POST.get('rut_dv')
        email = request.POST.get('email')
        password = request.POST.get('password')

        rut_completo = f"{rut_cuerpo}-{rut_dv}"

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este correo ya está registrado.')
            return redirect('registro')

        if Perfil.objects.filter(rut=rut_completo).exists():
            messages.error(request, 'Este RUT ya está registrado.')
            return redirect('registro')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        user.first_name = nombre
        user.save()

        Perfil.objects.create(
            usuario=user,
            rut=rut_completo,
            rol='Turista'
        )

        login(request, user)
        return redirect('habitaciones')

    return render(request, 'register.html')

# =========================
# LOGIN
# =========================
@redirect_if_authenticated
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('habitaciones')
        messages.error(request, 'Correo o contraseña incorrectos.')
        return redirect('login')
    return render(request, 'login.html')

# =========================
# DETALLE HABITACION
# =========================
def room_detail(request, hab_id):
    cancelar_reservas_expiradas()
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

# =========================
# RESERVA
# =========================
@login_required
def crear_reserva_provisional(request, id_habitacion):
    if request.method != 'POST':
        return redirect('habitaciones')
    
    hab = get_object_or_404(Habitacion, id_habitacion=id_habitacion)
    f_ingreso_str = request.POST.get('fecha_ingreso')
    f_salida_str = request.POST.get('fecha_salida')
    total_str = request.POST.get('total_estimado')

    if not f_ingreso_str or not f_salida_str or not total_str:
        messages.error(request, "Faltan datos.")
        return redirect('roomdetail', hab_id=id_habitacion)

    try:
        f_ingreso = datetime.strptime(f_ingreso_str, "%Y-%m-%d").date()
        f_salida = datetime.strptime(f_salida_str, "%Y-%m-%d").date()
        total = int(total_str)

        if f_salida <= f_ingreso:
            messages.error(request, "Fechas inválidas.")
            return redirect('roomdetail', hab_id=id_habitacion)

        existe = Reserva.objects.filter(
            habitacion=hab,
            estado_reserva__in=['Pendiente', 'Confirmada'],
            fecha_ingreso__lt=f_salida,
            fecha_salida__gt=f_ingreso
        ).exists()

        if existe:
            messages.warning(request, "Fechas no disponibles.")
            return redirect('roomdetail', hab_id=id_habitacion)

        reserva = Reserva.objects.create(
            usuario=request.user,
            habitacion=hab,
            fecha_ingreso=f_ingreso,
            fecha_salida=f_salida,
            total_estimado=total,  # ← guarda el número completo ej: 480000
            estado_reserva='Pendiente'
        )

        # ✅ Redirige a confirmar_pago_final en vez de renderizar directo
        return redirect('confirmar_pago_final', 
                        id_reserva=reserva.id_reserva, 
                        id_habitacion=id_habitacion)

    except Exception as e:
        print("ERROR REAL:", e)
        messages.error(request, "Error al crear reserva.")
        return redirect('roomdetail', hab_id=id_habitacion)

# =========================
# CONFIRMAR PAGO
# =========================
@login_required
def confirmar_pago_final(request, id_reserva, id_habitacion):
    habitacion = get_object_or_404(Habitacion, id_habitacion=id_habitacion)

    try:
        reserva = Reserva.objects.get(id_reserva=id_reserva)
    except Reserva.DoesNotExist:
        messages.error(request, "El tiempo de reserva ha expirado. Por favor, intenta reservar de nuevo.")
        return redirect('roomdetail', hab_id=id_habitacion)

    # Calcular noches
    delta = reserva.fecha_salida - reserva.fecha_ingreso
    noches = delta.days if delta.days > 0 else 1

    # Calcular montos
    total = reserva.total_estimado
    parcial = round(float(total) * 0.3, 2)

    if request.method == 'POST':
        metodo = request.POST.get('metodo_pago', 'Tarjeta')

        Pago.objects.create(
            id_reserva=reserva.id_reserva,
            monto_pagado=parcial,
            metodo_pago=metodo,
            fecha_pago=datetime.now(),
        )

        reserva.estado_reserva = 'Confirmada'
        reserva.save()

        messages.success(request, "¡Pago procesado con éxito! Te esperamos en Pacific Reef.")
        return redirect('habitaciones')

    context = {
        'reserva': reserva,
        'hab': habitacion,
        'noches': noches,
        'total': int(total),
        'parcial': int(parcial),
    }

    return render(request, 'pago.html', context)

# =========================
# PERFIL Y ADMIN (Resto de tu código igual)
# =========================
@login_required(login_url='login')
def perfil_usuario(request):
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)

    reservas = Reserva.objects.filter(
        usuario=request.user,
        estado_reserva='Confirmada'
    ).order_by('-fecha_creacion')

    if request.method == 'POST':
        if 'foto_perfil' in request.FILES:
            perfil.foto_perfil = request.FILES['foto_perfil']
            perfil.save()
            messages.success(request, '¡Foto actualizada!')
            return redirect('perfil_usuario')

    return render(request, 'user.html', {
        'perfil': perfil,
        'reservas': reservas
    })

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
    return render(request, 'form_habitacion.html', {'form': form, 'titulo': 'Nueva Habitación'})

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
    return render(request, 'form_habitacion.html', {'form': form, 'titulo': 'Editar Habitación'})

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Verificamos si el usuario tiene un perfil y si es Administrador
        if hasattr(request.user, 'perfil') and request.user.perfil.rol == 'Administrador':
            return view_func(request, *args, **kwargs)
        
        messages.error(request, "Acceso denegado. Se requieren permisos de Administrador.")
        return redirect('index') # O a donde quieras mandarlos
    return _wrapped_view

@login_required
@admin_required
def dashboard_admin(request):
    # Dinero total histórico
    total_historico = Pago.objects.aggregate(Sum('monto_pagado'))['monto_pagado__sum'] or 0

    # Ganancias por Año
    por_anio = Pago.objects.annotate(periodo=TruncYear('fecha_pago'))\
                           .values('periodo')\
                           .annotate(total=Sum('monto_pagado'))\
                           .order_by('-periodo')

    # Ganancias por Mes
    por_mes = Pago.objects.annotate(periodo=TruncMonth('fecha_pago'))\
                          .values('periodo')\
                          .annotate(total=Sum('monto_pagado'))\
                          .order_by('-periodo')[:12] # Últimos 12 meses

    # Ganancias por Día
    por_dia = Pago.objects.annotate(periodo=TruncDay('fecha_pago'))\
                          .values('periodo')\
                          .annotate(total=Sum('monto_pagado'))\
                          .order_by('-periodo')[:7] # Última semana

    context = {
        'total_historico': total_historico,
        'por_anio': por_anio,
        'por_mes': por_mes,
        'por_dia': por_dia,
    }
    return render(request, 'admin_dashboard.html', context)