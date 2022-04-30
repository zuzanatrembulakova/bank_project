from django.urls import path
from . import views, views_api

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

        path('api/external_transaction/', views_api.ExternalTransaction.as_view()),

        path('request_loan/', views.request_loan, name='request_loan'),
        path('decline_loan/', views.decline_loan, name='decline_loan'),
        path('accept_loan/', views.accept_loan, name='accept_loan'),
        path('pay_loan/', views.pay_loan, name='pay_loan'),
        path('del_loan/', views.del_loan, name='del_loan'),
]
