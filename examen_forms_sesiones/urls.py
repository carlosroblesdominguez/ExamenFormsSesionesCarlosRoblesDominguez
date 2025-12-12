from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ----------------------------
    # Index
    # ----------------------------
    path('', views.index, name='index'),

    # ----------------------------
    # Autenticación
    # ----------------------------
    path('signup/', views.registrar_usuario, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='examen_forms_sesiones/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),

    # ----------------------------
    # CRUD Ensayos Clínicos
    # ----------------------------
    path('ensayos_clinicos/crear/', views.ensayoclinico_create, name='ensayoclinico_create'),
    path('ensayos_clinicos/listar/', views.ensayoclinico_buscar, name='lista_ensayos_clinicos'),
    path('ensayos_clinicos/editar/<int:ensayoclinico_id>/', views.ensayoclinico_editar, name='ensayoclinico_editar'),
    path('ensayos_clinicos/eliminar/<int:ensayoclinico_id>/', views.ensayoclinico_eliminar, name='ensayoclinico_eliminar'),
]