from django import forms
from datetime import date
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *

# Formulario de registro
class RegistroForm(UserCreationForm):
    roles=(
        (Usuario.PACIENTE,'paciente'),
        (Usuario.INVESTIGADOR,'investigador'),
    )
    rol=forms.ChoiceField(choices=roles)
    edad=forms.IntegerField(required=False, label='Edad (sólo para pacientes)')
    class Meta:
        model = Usuario
        fields=('username','edad','email','password1','password2','rol')

# Formulario de Ensayo Clínico
class EnsayoClinicoModelForm(forms.ModelForm):
    # Campo usuarios personalizado (fuera de Meta)
    usuarios = forms.ModelMultipleChoiceField(
        queryset=Usuario.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False
    )

    class Meta:
        model = EnsayoClinico
        fields = ['nombre', 'descripcion', 'farmaco', 'pacientes', 'nivel_seguimiento', 'fecha_inicio', 'fecha_fin', 'activo']
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'farmaco': 'Fármaco',
            'pacientes': 'Pacientes',
            'nivel_seguimiento': 'Nivel de seguimiento',
            'fecha_inicio': 'Fecha de inicio',
            'fecha_fin': 'Fecha de fin',
            'activo': 'Está activo',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'farmaco': forms.Select(attrs={'class': 'form-select'}),
            'pacientes': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'nivel_seguimiento': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        descripcion = cleaned_data.get('descripcion')
        farmaco = cleaned_data.get('farmaco')
        pacientes = cleaned_data.get('pacientes')
        nivel_seguimiento = cleaned_data.get('nivel_seguimiento')
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        # Nombre único ignorando el propio registro
        ensayoclinico_id = self.instance.id if self.instance else None
        if nombre and EnsayoClinico.objects.filter(nombre=nombre).exclude(id=ensayoclinico_id).exists():
            self.add_error('nombre', "Ya existe un ensayo clínico con este nombre.")

        # Descripción mínima 100 caracteres
        if descripcion and len(descripcion) < 100:
            self.add_error('descripcion', "La descripción debe tener al menos 100 caracteres.")

        # Farmaco permite promociones
        if farmaco and not farmaco.puede_tener_promociones:
            self.add_error('farmaco', "Este fármaco no permite promociones.")

        # Pacientes mayores de edad
        if pacientes:
            for u in pacientes:
                if u.edad is not None and u.edad < 18:
                    self.add_error('pacientes', f"El paciente {u.username} no es mayor de edad.")

        # Nivel de seguimiento entre 0 y 10
        if nivel_seguimiento is not None and (nivel_seguimiento < 0 or nivel_seguimiento > 10):
            self.add_error('nivel_seguimiento', "El nivel de seguimiento debe estar entre 0 y 10.")

        # Fecha inicio < fecha fin
        if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
            self.add_error('fecha_inicio', "La fecha de inicio debe ser menor que la fecha de fin.")

        # Fecha fin ≥ hoy
        if fecha_fin and fecha_fin < date.today():
            self.add_error('fecha_fin', "La fecha de fin no puede ser anterior a hoy.")

        return cleaned_data
    
class EnsayoClinicoBusquedaForm(forms.Form):
    nombre = forms.CharField(required=False, label='Nombre o Descripción', widget=forms.TextInput(attrs={'class': 'form-control'}))
    fecha_fin_desde = forms.DateField(required=False, label='Fecha fin desde', widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    fecha_fin_hasta = forms.DateField(required=False, label='Fecha fin hasta', widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    nivel_seguimiento = forms.IntegerField(required=False, label='Nivel de seguimiento mínimo', widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}))
    pacientes = forms.ModelMultipleChoiceField(
        queryset=Paciente.objects.all(),
        required=False,
        label='Pacientes',
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    activo = forms.BooleanField(required=False, label='Está activo', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def clean(self):
        cleaned_data = super().clean()
        nivel_seguimiento = cleaned_data.get('nivel_seguimiento')
        fecha_fin_desde = cleaned_data.get('fecha_fin_desde')
        fecha_fin_hasta = cleaned_data.get('fecha_fin_hasta')
        
        # Nivel de seguimiento entre 0 y 10
        if nivel_seguimiento is not None and (nivel_seguimiento < 0 or nivel_seguimiento > 10):
            self.add_error('nivel_seguimiento', "El nivel de seguimiento debe estar entre 0 y 10.")
        
        # Fecha desde no mayor que fecha hasta
        if fecha_fin_desde and fecha_fin_hasta:
            if fecha_fin_desde > fecha_fin_hasta:
                self.add_error('fecha_fin_desde', "La fecha fin desde no puede ser mayor que la fecha fin hasta.")
                self.add_error('fecha_fin_hasta', "La fecha fin hasta no puede ser menor que la fecha fin desde.")    
        
        # nombre no puede ser mas de 100 caracteres
        nombre = cleaned_data.get('nombre')
        if nombre and len(nombre) > 100:
            self.add_error('nombre', "El nombre no puede tener más de 100 caracteres.")
            
        # fecha fin desde no puede ser menor a hoy
        if fecha_fin_desde and fecha_fin_desde < date.today():
            self.add_error('fecha_fin_desde', "La fecha fin desde no puede ser anterior a hoy.")
        
        return cleaned_data