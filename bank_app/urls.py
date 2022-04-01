from django.urls import path
from . import views

app_name = 'bank_app'

urlpatterns = [
        path('', views.index, name='index'),

        path('login/', views.login, name='login'),
        path('logout/', views.logout, name='logout'),

        path('create_customer/', views.create_customer, name='create_customer'),
        path('del_customer/', views.del_customer, name='del_customer'),
        path('update_ranking/', views.update_ranking, name='update_ranking'),

        path('accounts/', views.accounts, name='accounts'),
        path('add_account/', views.add_account, name='add_account'),
        path('del_account/', views.del_account, name='del_account'),

        path('show_movements/', views.show_movements, name='show_movements'),
        path('transfer_money/', views.transfer_money, name='transfer_money'),
]
