from django.db import models

class Habitacion(models.Model):
    id_habitacion = models.AutoField(primary_key=True)
    numero = models.CharField(max_length=10, unique=True)
    categoria = models.CharField(max_length=50)
    capacidad = models.IntegerField()
    precio_diario = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, default='Disponible')
    descripcion = models.TextField(null=True, blank=True)
    
    # --- NUEVO CAMPO PARA AMAZON S3 ---
    imagen = models.ImageField(upload_to='habitaciones/', null=True, blank=True)

    class Meta:
        managed = False 
        db_table = 'habitaciones'

    def __str__(self):
        return f"Hab {self.numero} - {self.categoria}"

class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    # Vinculamos al ID del usuario que se registró
    id_usuario = models.IntegerField() 
    habitacion = models.ForeignKey(Habitacion, on_delete=models.DO_NOTHING, db_column='id_habitacion')
    fecha_ingreso = models.DateField()
    fecha_salida = models.DateField()
    estado_reserva = models.CharField(max_length=20, default='Pendiente')
    total_estimado = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'reservas'