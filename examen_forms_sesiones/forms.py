from django import forms
from datetime import date
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *

# Formulario de registro
class RegistroForm(UserCreationForm):
    roles=(
        (Usuario.CLIENTE,'cliente'),
        (Usuario.STAFF,'staff'),
    )
    rol=forms.ChoiceField(choices=roles)
    class Meta:
        model = Usuario
        fields=('username','email','password1','password2','rol')
        
class PromocionModelForm(forms.ModelForm):
    # Campo usuarios personalizado (fuera de Meta)
    usuarios = forms.ModelMultipleChoiceField(
        queryset=Usuario.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False
    )

    class Meta:
        model = Promocion
        fields = ['nombre', 'descripcion', 'producto', 'usuarios', 'descuento', 'fecha_inicio', 'fecha_fin', 'esta_activa']
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'producto': 'Producto',
            'usuarios': 'Usuarios',
            'descuento': 'Descuento',
            'fecha_inicio': 'Fecha de inicio',
            'fecha_fin': 'Fecha de fin',
            'esta_activa': 'Está activa',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'esta_activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        descripcion = cleaned_data.get('descripcion')
        producto = cleaned_data.get('producto')
        usuarios = cleaned_data.get('usuarios')
        descuento = cleaned_data.get('descuento')
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        # Nombre único ignorando el propio registro
        promocion_id = self.instance.id if self.instance else None
        if nombre and Promocion.objects.filter(nombre=nombre).exclude(id=promocion_id).exists():
            self.add_error('nombre', "Ya existe una promoción con este nombre.")

        # Descripción mínima 100 caracteres
        if descripcion and len(descripcion) < 100:
            self.add_error('descripcion', "La descripción debe tener al menos 100 caracteres.")

        # Producto permite promociones
        if producto and not producto.puede_tener_promociones:
            self.add_error('producto', "Este producto no permite promociones.")

        # Usuarios mayores de edad
        if usuarios:
            for u in usuarios:
                if u.edad is not None and u.edad < 18:
                    self.add_error('usuarios', f"El usuario {u.username} no es mayor de edad.")

        # Descuento entre 0 y 10
        if descuento is not None and (descuento < 0 or descuento > 10):
            self.add_error('descuento', "El descuento debe estar entre 0 y 10.")

        # Fecha inicio < fecha fin
        if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
            self.add_error('fecha_inicio', "La fecha de inicio debe ser menor que la fecha de fin.")

        # Fecha fin ≥ hoy
        if fecha_fin and fecha_fin < date.today():
            self.add_error('fecha_fin', "La fecha de fin no puede ser anterior a hoy.")

        return cleaned_data