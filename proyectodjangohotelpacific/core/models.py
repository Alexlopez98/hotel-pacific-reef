from django.db import models
from django.contrib.auth.models import User

# --- MODELO DE PERFIL (Reemplaza a tu antiguo modelo Usuario) ---
class Perfil(models.Model):
    ROLES_CHOICES = [
        ('Turista', 'Turista'),
        ('Administrador', 'Administrador'),
    ]

    id_perfil = models.AutoField(primary_key=True)
    # Vinculamos 1 a 1 con el usuario interno de Django
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, db_column='ID_USUARIO')
    
    rut = models.CharField(max_length=12, unique=True)
    rol = models.CharField(max_length=20, choices=ROLES_CHOICES, default='Turista')
    # Sube la imagen a la carpeta usuarios/perfiles/ en tu S3
    foto_perfil = models.ImageField(upload_to='usuarios/perfiles/', null=True, blank=True, db_column='FOTO_PERFIL_URL')

    class Meta:
        managed = False # Recuerda crear la tabla PERFILES en Oracle
        db_table = 'perfiles'

    def __str__(self):
        return f"Perfil de {self.usuario.first_name} - RUT: {self.rut}"


# --- MODELOS DE NEGOCIO (Intactos) ---
class Habitacion(models.Model):
    id_habitacion = models.AutoField(primary_key=True)
    numero = models.CharField(max_length=10, unique=True)
    categoria = models.CharField(max_length=50)
    capacidad = models.IntegerField()
    precio_diario = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, default='Disponible')
    descripcion = models.TextField(null=True, blank=True)
    imagen = models.ImageField(upload_to='habitaciones/', null=True, blank=True)

    class Meta:
        managed = False 
        db_table = 'habitaciones'

    def __str__(self):
        return f"Hab {self.numero} - {self.categoria}"

class HabitacionImagen(models.Model):
    id_imagen = models.AutoField(primary_key=True)
    habitacion = models.ForeignKey(
        Habitacion, 
        related_name='imagenes_extra', 
        on_delete=models.CASCADE, 
        db_column='id_habitacion' 
    )
    imagen = models.ImageField(upload_to='habitaciones/extra/', db_column='IMAGEN_URL')

    class Meta:
        managed = False
        db_table = 'habitacion_imagenes' 

    def __str__(self):
        return f"Imagen extra de Hab {self.habitacion.numero}"

class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    id_usuario = models.IntegerField() 
    habitacion = models.ForeignKey(Habitacion, on_delete=models.DO_NOTHING, db_column='id_habitacion')
    fecha_ingreso = models.DateField()
    fecha_salida = models.DateField()
    estado_reserva = models.CharField(max_length=20, default='Pendiente')
    total_estimado = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'reservas'


class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    id_reserva = models.IntegerField(db_column='id_reserva')
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, db_column='monto_pagado')
    metodo_pago = models.CharField(max_length=50)
    fecha_pago = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'pagos'