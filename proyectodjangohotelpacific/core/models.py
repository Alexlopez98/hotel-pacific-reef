from django.db import models

class Habitacion(models.Model):
    id_habitacion = models.AutoField(primary_key=True)
    numero = models.CharField(max_length=10, unique=True)
    categoria = models.CharField(max_length=50)
    
    # Esta es la nueva columna. Le ponemos null=True y blank=True por si 
    # en el futuro creas una habitación y olvidas ponerle descripción.
    descripcion = models.CharField(max_length=250, null=True, blank=True) 
    
    capacidad = models.IntegerField()
    precio_diario = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'habitaciones'