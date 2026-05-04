from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Públicas y Autenticación
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='registro'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Habitaciones y Reservas
    path('habitaciones/', views.rooms_view, name='habitaciones'),
    path('habitacion/<int:hab_id>/', views.room_detail, name='roomdetail'),
    path('reservar/provisional/<int:id_habitacion>/', views.crear_reserva_provisional, name='crear_reserva_provisional'),
    path('reservar/confirmar/<int:id_reserva>/<int:id_habitacion>/', views.confirmar_pago_final, name='confirmar_pago_final'),

    # Perfil Turista
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('actualizar-perfil/', views.actualizar_perfil_ajax, name='actualizar_perfil_ajax'),

    # Dashboard Admin
    path('panel-admin/', views.dashboard_admin, name='dashboard_admin'),
    path('habitaciones/nueva/', views.agregar_habitacion, name='agregar_habitacion'),
    path('habitaciones/editar/<int:id>/', views.editar_habitacion, name='editar_habitacion'),

    # API AJAX para Admin
    path('api/admin/cambiar-estado/', views.api_cambiar_estado_reserva, name='api_cambiar_estado'),
    path('api/admin/eliminar-reserva/', views.api_eliminar_reserva, name='api_eliminar_reserva'),
    path('api/admin/buscar-historial/', views.api_buscar_historial, name='api_buscar_historial'),
]