from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(EnsayoClinico)
admin.site.register(Farmaco)
admin.site.register(Usuario)
admin.site.register(Paciente)
admin.site.register(Investigador)