from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponseRedirect
from django.db import IntegrityError, transaction
from datetime import datetime, timedelta
from django.contrib.auth.models import User

import pytz
import requests
from .views_common import *
from .models import *


def index(request):
    return show_index(request)


def show_index(request, message = '', is_error = False):
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
            loans = Loan.objects.filter(customer=active_customer)

            balances = []
            for a in customer_accounts.iterator():
                balance = get_balance_for_account(a)
                balances.append( (a.pk, balance) )
            
            context['customer_accounts'] = customer_accounts
            context['active_customer'] = active_customer
            context['balances'] = balances
            context['loans'] = loans

    return render(request, 'bank_app/index.html', context)


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
    customer.ranking = Ranking.objects.get(pk=selection)
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
        loans = Loan.objects.filter(customer=customer)

        balances = []
        for a in accounts.iterator():
            balance = get_balance_for_account(a)
            balances.append( (a.pk, balance) )

        context = {
                'usertype': get_user_type(request.user),
                'customer': customer,
                'accounts': accounts,
                'balances': balances,
                'loans': loans,
        }

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


def set_transaction(request):
    message = ''

    if request.method == "POST":

        from_accountpk = request.POST['from_account']
        from_account = Account.objects.get(pk = from_accountpk)

        amount = int(request.POST['amount'])
        description = request.POST['description']

        to_account = request.POST['to_account']

        if request.POST.get('payment_check'):
            repeat_number = int(request.POST['repeat_number'])
            repeat_time_unit = request.POST['repeat_time_unit']
            repeat_every = int(request.POST['repeat_every'])

            if repeat_time_unit == 'hour':
                repeat_every = repeat_every*60

            aut_payment = AutomaticPayment()
            aut_payment.account = from_account
            aut_payment.to_account = to_account
            aut_payment.value = amount
            aut_payment.description = description
            aut_payment.repeat_number = repeat_number
            aut_payment.repeat_every = repeat_every
            aut_payment.save()

        
        transaction_result = transfer_money(from_account, amount, description, to_account)

        if transaction_result == None:
            message = ''
        else:
            print('****', transaction_result)
            
    return show_index(request, message)


def do_automatic_payment():
    print('Spustam cron')

    aut_payments = AutomaticPayment.objects.filter(repeat_number__gt = 0)

    for ap in aut_payments.iterator():
        
        tz=pytz.timezone("utc")
        time = ap.timestamp + timedelta(minutes=ap.repeat_every)

        if time < datetime.now(tz):
            
            transfer_money(ap.account, ap.value, ap.description, ap.to_account)

            ap.timestamp = datetime.now(tz)
            ap.repeat_number = ap.repeat_number - 1
            ap.save()
    
    return 


@transaction.atomic 
def transfer_money(from_account, amount, description, to_account):
    message = 'Success'
    is_error = False

    try:
        dest_account = Account.objects.get(accountNumber = to_account)
    except:
        dest_account = None

    if get_balance_for_account(from_account) < amount:
        return 'Insufficient funds' 

    if not dest_account:
        bank_code = to_account[0:4]

        bank = Bank.objects.get(bankCode = bank_code)
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
            is_error = True
            message = response.json()['res']

    else: 
        # Dest account exists in our bank
        try:
            with transaction.atomic():
                movement_from = AccountMovement()
                movement_from.account = from_account
                movement_from.value = -amount
                movement_from.description = description
                movement_from.save()

                movement_to = AccountMovement()
                movement_to.account = dest_account
                movement_to.value = amount
                movement_to.description = description
                movement_to.save()

        except IntegrityError:
            is_error = True
            message = 'Transaction failed'
    
    print('Transfer money result: ', message, is_error)
    return None if is_error == False else message 


def request_loan(request):
    pk = request.POST['pk']
 
    loan = Loan()
    loan.customer = Customer.objects.get(user = request.user)
    loan.account = Account.objects.get(pk=pk)
    loan.loanAmount = request.POST['loan_amount']
    loan.remainingAmount = request.POST['loan_amount']
    loan.save()
 
    return HttpResponseRedirect(reverse('bank_app:index'))


@transaction.atomic
def accept_loan(request):
    # message = 'Success'
    # is_error = False

    if request.method == "POST":
        pk = request.POST['pk']
        pkcust = request.POST['pkcust']
        amount = int(request.POST['loan_amount'])
        to_account = request.POST['to_account']
        dest_account = Account.objects.filter(accountNumber = to_account)
        
        loan = Loan.objects.get(pk = pk)

        try:
            with transaction.atomic():
                movement_to = AccountMovement()
                movement_to.account = dest_account[0]
                movement_to.value = amount
                movement_to.description = 'Loan'
                movement_to.save()

                loan.confirmed = 'true'
                loan.save()

        except IntegrityError:
            message = 'Transaction failed'
            is_error = True
            print('Transaction failed')

    return show_accounts(request, pkcust)


def decline_loan(request):
    pk = request.POST['pk']
    pkcust = request.POST['pkcust']

    loan = Loan.objects.get(pk = pk)
    loan.confirmed = 'false'
    loan.save()

    return show_accounts(request, pkcust)


@transaction.atomic 
def pay_loan(request):
    message = 'Success'
    is_error = False

    if request.method == "POST":
        pk = request.POST['pk']
        account = request.POST['account']
        from_account = Account.objects.get(accountNumber = account)
        remaining_amount = int(request.POST['remaining_amount'])
        amount = int(request.POST['loan_transfer'])
        from_balance = get_balance_for_account(from_account)
        loan = Loan.objects.get(pk = pk)

        if amount > remaining_amount:
            print('The entered amount exceeds the loan')
        
        elif from_balance > amount:

            try:
                with transaction.atomic():
                    movement_from = AccountMovement()
                    movement_from.account = from_account
                    movement_from.value = -amount
                    movement_from.description = 'Loan payment'
                    movement_from.save()

                    loan.remainingAmount = remaining_amount - amount
                    loan.save()

            except IntegrityError:
                message = 'Transaction  failed'
                is_error = True
                print('Transaction failed')

        else:
            print('Insufficient funds')

    return show_index(request, message, is_error)


def del_loan(request):
    pk = request.POST['pk']
    pkcust = request.POST['pkcust']

    loan = get_object_or_404(Loan, pk=pk)
    loan.delete()
    
    return show_accounts(request, pkcust)
