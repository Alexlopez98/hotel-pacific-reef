from django import forms
from .models import Habitacion

class HabitacionForm(forms.ModelForm):
    class Meta:
        model = Habitacion
        # Agregamos 'descripcion' a la lista de campos
        fields = ['numero', 'categoria', 'capacidad', 'precio_diario', 'estado', 'descripcion', 'imagen']
        
        widgets = {
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 101'
            }),
            'categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Suite Presidencial'
            }),
            'capacidad': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'precio_diario': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'estado': forms.Select(choices=[
                ('Disponible', 'Disponible'),
                ('Ocupada', 'Ocupada'),
                ('Mantenimiento', 'Mantenimiento')
            ], attrs={'class': 'form-select'}),
            
            # Widget para el nuevo campo de descripción
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe las características de la habitación (Vista al mar, tipo de cama, etc.)'
            }),
            
            # Input de archivo para Amazon S3
            'imagen': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }