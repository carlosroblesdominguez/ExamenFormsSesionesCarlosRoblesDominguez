from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    CLIENTE = 1
    STAFF = 2
    ROLES = (
        (CLIENTE, 'cliente'),
        (STAFF, 'staff'),
    )
    rol = models.PositiveSmallIntegerField(choices=ROLES, default=CLIENTE)

class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

class Staff(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    puede_tener_promociones = models.BooleanField()

    def __str__(self):
        return self.nombre

class Promocion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuarios = models.ManyToManyField(Usuario)
    descuento = models.IntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    esta_activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre