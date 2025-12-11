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
    # CRUD Promociones
    # ----------------------------
    path('promociones/crear/', views.promocion_create, name='promocion_create'),
    path('promociones/listar/', views.promocion_buscar, name='lista_promociones'),
    path('promociones/editar/<int:promocion_id>/', views.promocion_editar, name='promocion_editar'),
    path('promociones/eliminar/<int:promocion_id>/', views.promocion_eliminar, name='promocion_eliminar'),
]