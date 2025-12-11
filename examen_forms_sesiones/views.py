from django.shortcuts import render, redirect
from django.db.models import Prefetch, Count, Max, Q
from django.contrib import messages
from .models import *
from .forms import *
from datetime import datetime, date, time
from django.contrib.auth import login

# Create your views here.
def index(request):
    if(not "fecha_inicio" in request.session):
        request.session["fecha_inicio"]=datetime.now().strftime('%d/%m/%Y %H:%M')
    return render(request, 'examen_forms_sesiones/index.html')

# ----------------
# Autenticacion 
# ----------------
def registrar_usuario(request):
    if request.method=='POST':
        formularioRegistro = RegistroForm(request.POST)
        if formularioRegistro.is_valid():
            user=formularioRegistro.save()
            rol=int(formularioRegistro.cleaned_data.get('rol'))
            
            if(rol==Usuario().ARBITRO):
                arbitro=Arbitro.objects.create(usuario=user)
                arbitro.save()
            elif(rol==Usuario().MANAGER):
                manager=Manager.objects.create(usuario=user)
                manager.save()
            return redirect('login')
    else:
        formularioRegistro=RegistroForm()
    return render(request, 'registration/signup.html',{'formularioRegistro':formularioRegistro})