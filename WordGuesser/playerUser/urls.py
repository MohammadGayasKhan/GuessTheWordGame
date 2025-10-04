from django.urls import path, include
from . import views

app_name='playerUser'

urlpatterns = [
    path('',views.home, name='home'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('game/', views.game, name='game'),
    path('signout/', views.signout, name='signout'),
    path('restart/', views.restart, name='restart')
]