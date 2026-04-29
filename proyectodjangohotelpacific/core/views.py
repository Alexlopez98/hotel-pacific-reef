from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages 
from .models import Habitacion # Importamos la tabla conectada a Oracle

def index_view(request):
    return render(request, 'index.html')

def rooms_view(request):
    # Traemos todas las habitaciones de Oracle Cloud
    lista_habitaciones = Habitacion.objects.all()
    
    return render(request, 'rooms.html', {
        'habitaciones': lista_habitaciones
    })

def register_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_completo')
        email = request.POST.get('email')
        password = request.POST.get('password')
        rut_cuerpo = request.POST.get('rut_cuerpo')
        
        # Validamos que el correo no exista ya
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este correo ya está registrado.')
            return redirect('registro') 
            
        # Creamos el usuario (username = email)
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = nombre
        user.save()
        
        # Logueamos automáticamente tras registrarse
        login(request, user)
        
        # Lo enviamos a ver las habitaciones
        return redirect('habitaciones')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Autenticamos usando email como username
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Login exitoso
            login(request, user)
            return redirect('habitaciones')
        else:
            # Error de credenciales
            messages.error(request, 'Correo o contraseña incorrectos.')
            return redirect('login')

    return render(request, 'login.html')