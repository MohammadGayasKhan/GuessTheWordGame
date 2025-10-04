from django.urls import path, include
from . import views

app_name='adminUser'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('signout/', views.signout, name='signout'),
    path('report/', views.report, name='report')
]