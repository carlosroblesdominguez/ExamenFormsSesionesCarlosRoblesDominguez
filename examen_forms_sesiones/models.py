from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    PACIENTE = 1
    INVESTIGADOR = 2
    ROLES = (
        (PACIENTE, 'paciente'),
        (INVESTIGADOR, 'investigador'),
    )
    rol = models.PositiveSmallIntegerField(choices=ROLES, default=PACIENTE)
    
    # FUNCIONES PERSONALIZADAS PARA SABER EL ROL DEL USUARIO (PERMISOS)
    def es_paciente(self):
        return self.groups.filter(name='Pacientes').exists()
    
    def es_investigador(self):
        return self.groups.filter(name='Investigadores').exists()


# campo edad obligatorio para el registro de pacientes
class Paciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    edad = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
       return self.usuario.username
   
class Investigador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    def __str__(self):
       return self.usuario.username

class Farmaco(models.Model):
   nombre = models.CharField(max_length=100)
   apto_para_ensayos = models.BooleanField()
   def __str__(self):
       return self.nombre
   
class EnsayoClinico(models.Model):
   nombre = models.CharField(max_length=100)
   descripcion = models.TextField()
   farmaco = models.ForeignKey(Farmaco, on_delete=models.CASCADE)
   pacientes = models.ManyToManyField('Paciente')
   nivel_seguimiento = models.IntegerField()
   fecha_inicio = models.DateField()
   fecha_fin = models.DateField()
   activo = models.BooleanField(default=True)
   creado_por = models.ForeignKey('Investigador', on_delete=models.CASCADE)  
   
   def __str__(self):
       return self.nombre
