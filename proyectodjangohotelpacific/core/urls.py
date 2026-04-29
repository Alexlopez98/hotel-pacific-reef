from django.urls import path
from .views import index_view, login_view, register_view, rooms_view

urlpatterns = [
    path('', index_view, name='index'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='registro'), 
    path('habitaciones/', rooms_view, name='habitaciones')
]