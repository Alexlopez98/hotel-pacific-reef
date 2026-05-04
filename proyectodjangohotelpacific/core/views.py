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
from django.db.models import Sum, Q
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.http import JsonResponse
from django.views.decorators.http import require_POST

# =========================
# LÓGICA DE CANCELACIÓN
# =========================
def cancelar_reservas_expiradas():
    limite = timezone.now() - timedelta(seconds=10)
    Reserva.objects.filter(
        estado_reserva='Pendiente',
        fecha_creacion__lt=limite
    ).update(estado_reserva='Cancelada')
    
    eliminadas, _ = Reserva.objects.filter(estado_reserva='Cancelada').delete()
    if eliminadas > 0:
        print(f"DEBUG: Se eliminaron {eliminadas} registros obsoletos.")

# =========================
# DECORADORES (Seguridad y Redirección)
# =========================
def redirect_if_authenticated(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            # Si ya está logueado, lo mandamos a su lugar correspondiente
            if hasattr(request.user, 'perfil') and request.user.perfil.rol == 'Administrador':
                return redirect('dashboard_admin')
            else:
                return redirect('habitaciones')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Guardia de seguridad: Solo Administradores
        if hasattr(request.user, 'perfil') and request.user.perfil.rol == 'Administrador':
            return view_func(request, *args, **kwargs)
        messages.error(request, "Acceso denegado. Se requieren permisos de Administrador.")
        return redirect('index')
    return _wrapped_view

# =========================
# PUBLICAS Y REGISTRO
# =========================
@redirect_if_authenticated
def index_view(request):
    return render(request, 'index.html')

def rooms_view(request):
    cancelar_reservas_expiradas()
    lista_habitaciones = Habitacion.objects.all()
    return render(request, 'rooms.html', {'habitaciones': lista_habitaciones})

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
            messages.error(request, 'Este correo ya está registrado en nuestro sistema.')
            return redirect('registro')
            
        if Perfil.objects.filter(rut=rut_completo).exists():
            messages.error(request, 'Este RUT ya tiene una cuenta asociada.')
            return redirect('registro')

        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = nombre
        user.save()
        Perfil.objects.create(usuario=user, rut=rut_completo, rol='Turista')
        login(request, user)
        return redirect('habitaciones')
    return render(request, 'register.html')

@redirect_if_authenticated
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user:
            login(request, user)
            # Redirección inteligente tras hacer login exitoso
            if hasattr(user, 'perfil') and user.perfil.rol == 'Administrador':
                messages.success(request, f'¡Bienvenido al Panel de Administración, {user.first_name}!')
                return redirect('dashboard_admin')
            else:
                return redirect('habitaciones')
                
        messages.error(request, 'Correo o contraseña incorrectos.')
        return redirect('login')
    return render(request, 'login.html')

# =========================
# RESERVAS Y HABITACIONES
# =========================
def room_detail(request, hab_id):
    cancelar_reservas_expiradas()
    habitacion = get_object_or_404(Habitacion, id_habitacion=hab_id)
    reservas = Reserva.objects.filter(habitacion=habitacion, estado_reserva__in=['Confirmada', 'Pendiente'])
    fechas_bloqueadas = []
    for r in reservas:
        actual = r.fecha_ingreso
        while actual <= r.fecha_salida:
            fechas_bloqueadas.append(actual.strftime('%Y-%m-%d'))
            actual += timedelta(days=1)
    return render(request, 'roomdetail.html', {'hab': habitacion, 'fechas_bloqueadas': json.dumps(fechas_bloqueadas)})

@login_required
def crear_reserva_provisional(request, id_habitacion):
    if request.method != 'POST':
        return redirect('habitaciones')
    hab = get_object_or_404(Habitacion, id_habitacion=id_habitacion)
    f_ingreso_str = request.POST.get('fecha_ingreso')
    f_salida_str = request.POST.get('fecha_salida')
    total_str = request.POST.get('total_estimado')

    try:
        f_ingreso = datetime.strptime(f_ingreso_str, "%Y-%m-%d").date()
        f_salida = datetime.strptime(f_salida_str, "%Y-%m-%d").date()
        total = int(total_str)

        if f_salida <= f_ingreso:
            messages.error(request, "Fechas inválidas.")
            return redirect('roomdetail', hab_id=id_habitacion)

        existe = Reserva.objects.filter(
            habitacion=hab, estado_reserva__in=['Pendiente', 'Confirmada'],
            fecha_ingreso__lt=f_salida, fecha_salida__gt=f_ingreso
        ).exists()

        if existe:
            messages.warning(request, "Fechas no disponibles.")
            return redirect('roomdetail', hab_id=id_habitacion)

        reserva = Reserva.objects.create(
            usuario=request.user, habitacion=hab, fecha_ingreso=f_ingreso,
            fecha_salida=f_salida, total_estimado=total, estado_reserva='Pendiente'
        )
        return redirect('confirmar_pago_final', id_reserva=reserva.id_reserva, id_habitacion=id_habitacion)
    except Exception as e:
        messages.error(request, "Error al crear reserva.")
        return redirect('roomdetail', hab_id=id_habitacion)

@login_required
def confirmar_pago_final(request, id_reserva, id_habitacion):
    habitacion = get_object_or_404(Habitacion, id_habitacion=id_habitacion)
    try:
        reserva = Reserva.objects.get(id_reserva=id_reserva)
    except Reserva.DoesNotExist:
        messages.error(request, "El tiempo ha expirado.")
        return redirect('roomdetail', hab_id=id_habitacion)

    total = reserva.total_estimado
    parcial = round(float(total) * 0.3, 2)

    if request.method == 'POST':
        metodo = request.POST.get('metodo_pago', 'Tarjeta')
        Pago.objects.create(id_reserva=reserva.id_reserva, monto_pagado=parcial, metodo_pago=metodo, fecha_pago=datetime.now())
        reserva.estado_reserva = 'Confirmada'
        reserva.save()
        messages.success(request, "¡Pago procesado con éxito!")
        return redirect('habitaciones')

    return render(request, 'pago.html', {'reserva': reserva, 'hab': habitacion, 'total': int(total), 'parcial': int(parcial)})

# =========================
# PERFIL DE USUARIO
# =========================
@login_required(login_url='login')
def perfil_usuario(request):
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)
    reservas = Reserva.objects.filter(usuario=request.user, estado_reserva='Confirmada').order_by('-fecha_creacion')
    if request.method == 'POST':
        if 'foto_perfil' in request.FILES:
            perfil.foto_perfil = request.FILES['foto_perfil']
            perfil.save()
            messages.success(request, '¡Foto actualizada!')
            return redirect('perfil_usuario')
    return render(request, 'user.html', {'perfil': perfil, 'reservas': reservas})

# =========================
# AJAX ACTUALIZAR PERFIL INFO
# =========================
@login_required(login_url='login')
@require_POST
def actualizar_perfil_ajax(request):
    try:
        user = request.user
        nuevo_nombre = request.POST.get('first_name', '').strip()
        nuevo_apellido = request.POST.get('last_name', '').strip()
        user.first_name = nuevo_nombre
        user.last_name = nuevo_apellido
        user.save()
        return JsonResponse({'status': 'success', 'message': 'Perfil actualizado correctamente.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# =========================
# ADMIN Y DASHBOARD
# =========================
@login_required
@admin_required
def agregar_habitacion(request):
    if request.method == 'POST':
        form = HabitacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habitación creada con éxito en el sistema.')
            return redirect('dashboard_admin') # <-- Redirige de vuelta al panel
    else:
        form = HabitacionForm()
    return render(request, 'form_habitacion.html', {'form': form, 'titulo': 'Añadir Nueva Habitación'})

@login_required
@admin_required
def editar_habitacion(request, id):
    habitacion = get_object_or_404(Habitacion, id_habitacion=id)
    if request.method == 'POST':
        form = HabitacionForm(request.POST, instance=habitacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habitación actualizada correctamente.')
            return redirect('dashboard_admin') # <-- Redirige de vuelta al panel
    else:
        form = HabitacionForm(instance=habitacion)
    return render(request, 'form_habitacion.html', {'form': form, 'titulo': f'Editar Habitación {habitacion.numero}'})

@login_required
@admin_required
def dashboard_admin(request):
    # EL CAMBIO ESTÁ AQUÍ: Usamos __in para excluir una lista de estados
    reservas_activas = Reserva.objects.exclude(
        estado_reserva__in=['Finalizada', 'Cancelada']
    ).order_by('-fecha_creacion')

    # ... (El resto de la función sigue igual)
    for r in reservas_activas:
        r.abono_30 = int(float(r.total_estimado) * 0.3)
        r.saldo_70 = int(float(r.total_estimado)) - r.abono_30

    habitaciones_todas = Habitacion.objects.all()

    # 2. Cálculos financieros
    total_historico = Pago.objects.aggregate(Sum('monto_pagado'))['monto_pagado__sum'] or 0

    por_anio = Pago.objects.annotate(periodo=TruncYear('fecha_pago')).values('periodo').annotate(total=Sum('monto_pagado')).order_by('periodo')
    por_mes = Pago.objects.annotate(periodo=TruncMonth('fecha_pago')).values('periodo').annotate(total=Sum('monto_pagado')).order_by('periodo')[:12]
    por_dia = Pago.objects.annotate(periodo=TruncDay('fecha_pago')).values('periodo').annotate(total=Sum('monto_pagado')).order_by('periodo')[:7]

    # --- NUEVO: Traemos todo el historial de pagos (los últimos 100) ---
    historial_pagos = Pago.objects.all().order_by('-fecha_pago')[:100]

    chart_data = {
        'diario': {
            'labels': [p['periodo'].strftime('%d/%m') for p in por_dia],
            'data': [float(p['total']) for p in por_dia]
        },
        'mensual': {
            'labels': [p['periodo'].strftime('%b %Y') for p in por_mes],
            'data': [float(p['total']) for p in por_mes]
        },
        'anual': {
            'labels': [p['periodo'].strftime('%Y') for p in por_anio],
            'data': [float(p['total']) for p in por_anio]
        }
    }

    context = {
        'reservas': reservas_activas,
        'habitaciones': habitaciones_todas,
        'total_historico': total_historico,
        'chart_data': json.dumps(chart_data),
        'pagos': historial_pagos # <-- Lo enviamos al HTML
    }
    return render(request, 'admin_dashboard.html', context)

# =========================
# RUTAS AJAX PARA EL ADMIN
# =========================
@login_required
@admin_required
@require_POST
def api_cambiar_estado_reserva(request):
    try:
        data = json.loads(request.body)
        nuevo_estado = data.get('nuevo_estado')
        reserva = Reserva.objects.get(id_reserva=data.get('id_reserva'))
        
        reserva.estado_reserva = nuevo_estado
        reserva.save()

        mensaje_cobro = ""
        # LÓGICA FINANCIERA
        if nuevo_estado == 'Finalizada':
            pagado_hasta_ahora = Pago.objects.filter(id_reserva=reserva.id_reserva).aggregate(Sum('monto_pagado'))['monto_pagado__sum'] or 0
            restante = float(reserva.total_estimado) - float(pagado_hasta_ahora)
            
            if restante > 0:
                Pago.objects.create(
                    id_reserva=reserva.id_reserva,
                    monto_pagado=restante,
                    metodo_pago='Pago Final en Recepción',
                    fecha_pago=datetime.now()
                )
            # Preparamos el texto del saldo para la alerta
            mensaje_cobro = f"${restante:,.0f}".replace(',', '.')

        # NUEVO: Devolvemos los datos específicos de la habitación y cliente al JS
        return JsonResponse({
            'status': 'success', 
            'nuevo_estado': nuevo_estado,
            'cliente': f"{reserva.usuario.first_name} {reserva.usuario.last_name}",
            'hab_numero': reserva.habitacion.numero,
            'hab_categoria': reserva.habitacion.categoria,
            'saldo_cobrado': mensaje_cobro
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@admin_required
@require_POST
def api_eliminar_reserva(request):
    try:
        data = json.loads(request.body)
        reserva = Reserva.objects.get(id_reserva=data.get('id_reserva'))
        reserva.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@admin_required
def api_buscar_historial(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'reservas': []})

    usuarios_coincidentes = User.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query)
    ).values_list('id', flat=True)

    reservas = Reserva.objects.filter(usuario_id__in=usuarios_coincidentes).order_by('-fecha_ingreso')
    
    data = []
    for r in reservas:
        try:
            rut_cliente = r.usuario.perfil.rut
        except:
            rut_cliente = "No Registrado"
            
        # NUEVO: Calculamos exactamente cuánto pagó en la realidad
        pagado = Pago.objects.filter(id_reserva=r.id_reserva).aggregate(Sum('monto_pagado'))['monto_pagado__sum'] or 0
            
        data.append({
            'id_reserva': r.id_reserva,
            'cliente': f"{r.usuario.first_name} {r.usuario.last_name}",
            'rut': rut_cliente,
            'habitacion': f"N° {r.habitacion.numero} ({r.habitacion.categoria})",
            'ingreso': r.fecha_ingreso.strftime('%d/%m/%Y'),
            'salida': r.fecha_salida.strftime('%d/%m/%Y'),
            'total_estimado': f"${r.total_estimado:,.0f}".replace(',', '.'),
            'total_pagado': f"${pagado:,.0f}".replace(',', '.'), # Enviamos el dinero real
            'estado': r.estado_reserva
        })
    return JsonResponse({'reservas': data})