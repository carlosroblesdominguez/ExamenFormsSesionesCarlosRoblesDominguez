from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario

# Formulario de registro
class RegistroForm(UserCreationForm):
    roles=(
        (Usuario.MANAGER,'manager'),
        (Usuario.ARBITRO,'arbitro'),
    )
    rol=forms.ChoiceField(choices=roles)
    class Meta:
        model = Usuario
        fields=('username','email','password1','password2','rol')