from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class Usuario(AbstractUser):
    MANAGER=1
    ARBITRO=2
    ROLES=(
        (MANAGER,'manager'),
        (ARBITRO,'arbitro'),
    )
    
    rol=models.PositiveSmallIntegerField(
        choices=ROLES,default=0
    )

class Manager(models.Model):
    usuario=models.OneToOneField(Usuario,on_delete=models.CASCADE)
class Arbitro(models.Model):
    usuario=models.OneToOneField(Usuario,on_delete=models.CASCADE)