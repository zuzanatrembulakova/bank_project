from django.shortcuts import render, reverse
from django.shortcuts import render, get_object_or_404
from .models import *
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect
from django.db import IntegrityError, transaction

import requests

from .views_common import *

def index(request):
    return show_index(request)

def show_index(request, message='', is_error=False):
    context = {}

    if request.user.is_authenticated:

        rankings = Ranking.objects.all()

        context = {
            'usertype': get_user_type(request.user),
            'rankings': rankings,
            'message': message,
            'is_error': is_error,
        }

        if get_user_type(request.user) == 'BANKER':
            context['customers'] = Customer.objects.all()
            context['customer_count'] = Customer.objects.all().count()

        if get_user_type(request.user) == 'CUSTOMER':
            active_customer = Customer.objects.get(user = request.user)
            customer_accounts = Account.objects.filter(customer=active_customer) 

            balances = []
            for a in customer_accounts.iterator():
                balance = get_balance_for_account(a)
                balances.append( (a.pk, balance) )
            
            context['customer_accounts'] = customer_accounts
            context['active_customer'] = active_customer
            context['balances'] = balances

    return render(request, 'bank_app/index.html', context)

def login(request):
    context = {}
    if request.method == "POST":
        user = authenticate(request, username=request.POST['name'], password=request.POST['password'])
        userType = get_user_type(user)        
        if user:
            dj_login(request, user)
            print(f"Looged in as {userType}")
            return HttpResponseRedirect(reverse('bank_app:index'))
        else:
            print('Invalid Login')
            context = {                                                                             
                'error': 'Bad username or password.'
                }
    return render(request, 'bank_app/index.html', context)

def logout(request):
    dj_logout(request)
    return render(request, 'bank_app/index.html')

def create_customer(request):
    if request.method == "POST":
        user_name = request.POST['name']
        password = request.POST['password']
        phone = request.POST['phone']

        user = User.objects.create_user(user_name, email=None, password=password)
        
        if user:
            customer = Customer()
            customer.ranking = Ranking.objects.get(rType='Basic')
            customer.phone = phone
            customer.user = user
            customer.save()

    return HttpResponseRedirect(reverse('bank_app:index'))

def del_customer(request):
    pk = request.POST['pk']
    
    customer = get_object_or_404(Customer, pk=pk)
    User.objects.get(pk=customer.user.pk).delete()
    customer.delete()

    return HttpResponseRedirect(reverse('bank_app:index'))

def update_ranking(request):
    pk = request.POST['pk']
    selection = request.POST['ranking']

    customer = get_object_or_404(Customer, pk=pk)
    customer.ranking = Ranking.objects.get(rType=selection)
    customer.save()

    return HttpResponseRedirect(reverse('bank_app:index'))

def accounts(request):
    if request.method == "POST":
        pkcust = request.POST['pk']

    return show_accounts(request, pkcust)

def show_accounts(request, pkcust):
    context = {}

    if request.user.is_authenticated and get_user_type(request.user) == "BANKER":
        
        customer = get_object_or_404(Customer, pk=pkcust)
        accounts = Account.objects.filter(customer=customer)

        balances = []
        for a in accounts.iterator():
            balance = get_balance_for_account(a)
            balances.append( (a.pk, balance) )

    context = {
            'usertype': get_user_type(request.user),
            'customer': customer,
            'accounts': accounts,
            'balances': balances,
    }

    # print(account_movement)
    return render(request, 'bank_app/accounts.html', context)

def add_account(request):
    pkcust = request.POST['pk']

    account_number = request.POST['number']
    balance = request.POST['balance']

    customer = get_object_or_404(Customer, pk=pkcust)

    account = Account()
    account.customer = customer
    account.accountNumber = account_number
    account.save()

    account_movement = AccountMovement()
    account_movement.account = account
    account_movement.value = balance
    account_movement.description = "Initial balance"
    account_movement.save()

    return show_accounts(request, pkcust)

def del_account(request):
    pk = request.POST['pk']
    pkcust = request.POST['pk_cust']

    account = get_object_or_404(Account, pk=pk)
    account.delete()

    return show_accounts(request, pkcust)

def show_movements(request):
    context = {}
    
    pk = request.POST['pk']

    account = get_object_or_404(Account, pk=pk)
    balance = get_balance_for_account(account)
    account_movements = AccountMovement.objects.filter(account=account)

    context = {
            'usertype': get_user_type(request.user),
            'account': account,
            'balance': balance,
            'account_movements': account_movements,
    }

    return render(request, 'bank_app/movements.html', context)

@transaction.atomic 
def transfer_money(request):
    message = 'Success'
    is_error = False

    if request.method == "POST":

        from_accountpk = request.POST['from_account']
        from_account = get_object_or_404(Account, pk=from_accountpk)

        amount = int(request.POST['amount'])
        description = request.POST['description']

        from_balance = get_balance_for_account(from_account)

        to_account = request.POST['to_account']

        dest_account = Account.objects.filter(accountNumber = to_account)
        
        if not dest_account:
            bank_code = to_account[0:4]

            bank = get_object_or_404(Bank, bankCode = bank_code)
            url = 'http://' + bank.path + '/bank/api/external_transaction/'
            print(url)

            data = {
                    "to_account": to_account,
                    "amount": amount,
                    "description": description,
                    }
            print(data)

            response = requests.post(url, data=data)
            print(response.status_code)
            if response.status_code == 200:
                print('Success!')

                account_movement = AccountMovement()
                account_movement.account = from_account
                account_movement.value = -amount
                account_movement.description = description
                account_movement.save()

                message = response.json()['res']
            elif response.status_code == 404:
                print('Not Found.')
                message = response.json()['res']
        else: 
            print(dest_account)

            if from_balance > amount:

                try:
                    with transaction.atomic():
                        movement_from = AccountMovement()
                        movement_from.account = from_account
                        movement_from.value = -amount
                        movement_from.description = description
                        movement_from.save()

                        movement_to = AccountMovement()
                        movement_to.account = dest_account[0]
                        movement_to.value = amount
                        movement_to.description = description
                        movement_to.save()

                except IntegrityError:
                    message = 'Transaction failed'
                    is_error = True
                    print('Transaction failed')

            else:
                print('Insufficient funds')

    return show_index(request, message, is_error)



