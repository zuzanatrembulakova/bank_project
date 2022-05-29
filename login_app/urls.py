from django.urls import path
from . import views
from django.conf import settings    
from django.conf.urls.static import static  

app_name = 'login_app'

urlpatterns = [
        path('', views.login, name='login'),

        path('login/', views.login, name='login'),
        path('login_verify/', views.login_verify, name='login_verify'),
        path('logout/', views.logout, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)