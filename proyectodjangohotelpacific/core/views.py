from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages # Para enviar mensajes de error o éxito

def index_view(request):
    return render(request, 'index.html')

def rooms_view(request):
    return render(request, 'rooms.html')

def register_view(request):
    # Si el usuario hace clic en "Registrarse", la petición es POST
    if request.method == 'POST':
        # 1. Capturamos los datos usando los 'name' del HTML
        nombre = request.POST.get('nombre_completo')
        email = request.POST.get('email')
        password = request.POST.get('password')
        rut_cuerpo = request.POST.get('rut_cuerpo')
        
        # 2. Validamos que el correo no exista ya en la base de datos
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este correo ya está registrado.')
            return redirect('registro')
            
        # 3. Creamos el usuario. 
        # Nota: Django requiere un 'username', así que usaremos el email para eso.
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = nombre
        user.save()
        
        # 4. (Opcional) Logueamos al usuario automáticamente tras registrarse
        login(request, user)
        
        # 5. Lo redirigimos a la página de inicio o habitaciones
        return redirect('index')

    # Si la petición es GET (solo entró a la URL), le mostramos el formulario
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Intentamos autenticar al usuario (recuerda que seteamos el username como email)
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Si las credenciales son correctas, iniciamos sesión
            login(request, user)
            return redirect('index')
        else:
            # Si se equivoca en la clave o email
            messages.error(request, 'Correo o contraseña incorrectos.')
            return redirect('login')

    return render(request, 'login.html')