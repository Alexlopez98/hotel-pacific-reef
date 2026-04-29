from django.db import models

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
        db_column='id_habitacion' # Conecta con ID_HABITACION
    )
    # db_column le dice a Django el nombre real en Oracle
    imagen = models.ImageField(upload_to='habitaciones/extra/', db_column='IMAGEN_URL')

    class Meta:
        managed = False
        # Ajustado al nombre exacto de tu tabla en plural
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