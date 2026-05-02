from django import forms
from .models import Habitacion

class HabitacionForm(forms.ModelForm):
    class Meta:
        model = Habitacion
        # 1. Agregamos todos los nuevos campos h_ a la lista
        fields = [
            'numero', 'categoria', 'capacidad', 'precio_diario', 'estado', 
            'descripcion', 'imagen', 'h_ac', 'h_wifi', 'h_trabajo', 
            'h_tv', 'h_seguridad', 'h_mascotas', 'h_desayuno', 
            'h_vista_mar', 'h_limpieza'
        ]
        
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 101'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Suite Presidencial'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_diario': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(choices=[
                ('Disponible', 'Disponible'),
                ('Ocupada', 'Ocupada'),
                ('Mantenimiento', 'Mantenimiento')
            ], attrs={'class': 'form-select'}),
            
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe la esencia de la habitación...'
            }),
            
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),

            # --- NUEVOS WIDGETS PARA LOS SERVICIOS ---
            'h_ac': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'h_wifi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'h_trabajo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'h_tv': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'h_seguridad': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'h_desayuno': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'h_vista_mar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'h_limpieza': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            # Selector para Mascotas
            'h_mascotas': forms.Select(choices=[
                ('No permitido', 'No permitido'),
                ('Pequeño', 'Pequeño'),
                ('Mediano', 'Mediano'),
                ('Grande', 'Grande'),
            ], attrs={'class': 'form-select'}),
        }