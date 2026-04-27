from django.urls import path
from .views import index_view, login_view, register_view, rooms_view

urlpatterns = [
    path('', index_view),
    path('login/', login_view),
    path('register/', register_view),
    path('habitaciones/', rooms_view)
]