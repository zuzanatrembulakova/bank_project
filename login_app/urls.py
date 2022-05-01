from django.urls import path
from . import views

app_name = 'login_app'

urlpatterns = [
        path('', views.login, name='login'),

        path('login/', views.login, name='login'),
        path('login_verify/', views.login_verify, name='login_verify'),
        path('logout/', views.logout, name='logout'),
]