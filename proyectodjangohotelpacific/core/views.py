from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages 
from django.contrib.auth.decorators import login_required # Para proteger rutas de admin
from .models import Habitacion
from .forms import HabitacionForm # Asegúrate de crear este archivo

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
    # Usamos id_habitacion porque así está en tu script SQL
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