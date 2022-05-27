from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponseRedirect
from django.db import IntegrityError, transaction
from datetime import date, datetime, timedelta
from django.contrib.auth.models import User
 
import pytz
import requests
from .views_common import *
from .models import *
 
import random
 
 
def index(request):
    return show_index(request)
 
 
def show_index(request, message = '', is_error = False):
    context = {}
 
    if request.user.is_authenticated:
 
        rankings = Ranking.objects.all()
        currencies = Currency.objects.all()
 
        context = {
            'usertype': get_user_type(request.user),
            'rankings': rankings,
            'currencies': currencies,
            'message': message,
            'is_error': is_error,
        }
 
        if get_user_type(request.user) == 'BANKER':
            context['customers'] = Customer.objects.all()
            context['customer_count'] = Customer.objects.all().count()
 
        if get_user_type(request.user) == 'CUSTOMER':
            active_customer = Customer.objects.get(user=request.user)
            customer_accounts = Account.objects.filter(customer=active_customer)
            loans = LoanRequest.objects.filter(customer=active_customer)
            cards = CreditCard.objects.filter(customer=active_customer)
 
            balances = []
            for a in customer_accounts.iterator():
                balance = round(get_balance_for_account(a), 2)
                balances.append((a.pk, balance, a.currency))
            
            card_repay_balances = []
            for c in cards.iterator():
                card_repay_balance = round(get_repay_amount_for_card(c), 2)
                card_repay_balances.append((c.pk, card_repay_balance))
           
            context['customer_accounts'] = customer_accounts
            context['active_customer'] = active_customer
            context['balances'] = balances
            context['card_repay_balances'] = card_repay_balances
            context['loans'] = loans
            context['cards'] = cards
 
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
        currencies = Currency.objects.all() 
        accounts = Account.objects.filter(customer=customer)
        loans = LoanRequest.objects.filter(customer=customer)
        cards = CreditCard.objects.filter(customer=customer)
 
        balances = []
        for a in accounts.iterator():
            balance = round(get_balance_for_account(a), 2)
            balances.append((a.pk, balance, a.currency))
       
        card_repay_balances = []
        for c in cards.iterator():
            card_repay_balance = round(get_repay_amount_for_card(c), 2)
            account = Account.objects.get(accountNumber=c.account)
            card_repay_balances.append((c.pk, card_repay_balance, account.currency))
 
        context = {
                'usertype': get_user_type(request.user),
                'customer': customer,
                'accounts': accounts,
                'currencies': currencies,
                'balances': balances,
                'card_repay_balances': card_repay_balances,
                'loans': loans,
                'cards': cards,
        }
 
    return render(request, 'bank_app/accounts.html', context)
 
 
def add_account(request):
    pkcust = request.POST['pk']
 
    account_number = request.POST['number']
    balance = request.POST['balance']
    currencypk = request.POST['account_currency']
 
    customer = get_object_or_404(Customer, pk=pkcust)
    currency = Currency.objects.get(pk=currencypk)
 
    account = Account()
    account.customer = customer
    account.currency = currency
    account.accountNumber = account_number
    account.save()
 
    account_movement = AccountMovement()
    account_movement.account = account
    account_movement.fromAccount = 'Bank'
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
 
        amount = float(request.POST['amount'])
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
            aut_payment.toAccount = to_account
            aut_payment.value = amount
            aut_payment.description = description
            aut_payment.repeatNumber = repeat_number
            aut_payment.repeatEvery = repeat_every
            aut_payment.save()
 
       
        transaction_result = transfer_money(from_account, amount, description, to_account)
 
        if transaction_result == None:
            message = ''
        else:
            print('****', transaction_result)
           
    return show_index(request, message)

 
def do_automatic_payment():
 
    aut_payments = AutomaticPayment.objects.filter(repeatNumber__gt = 0)
 
    for ap in aut_payments.iterator():
       
        tz=pytz.timezone("utc")
        time = ap.timestamp + timedelta(minutes=ap.repeatEvery)
 
        if time < datetime.now(tz):
           
            if transfer_money(ap.account, ap.value, ap.description, ap.toAccount) == None:
                ap.timestamp = datetime.now(tz)
                ap.repeatNumber = ap.repeatNumber - 1
                ap.save()
    return
 
 
@transaction.atomic
def transfer_money(from_account, amount, description, to_account):
    message = 'Success'
    is_error = False

    from_account_number = from_account.accountNumber
 
    try:
        dest_account = Account.objects.get(accountNumber = to_account)
    except:
        dest_account = None
 
    if get_balance_for_account(from_account) < amount:
        return 'Insufficient funds'
 
    if not dest_account:
        bank_code = to_account[0:4]
 
        bank = Bank.objects.get(bankCode = bank_code)
        url = 'http://' + bank.path + '/bank_app/api/external_transaction/'
        print(url)
 
        data = {
                "to_account": to_account,
                "from_account": from_account_number,
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
            account_movement.fromAccount = to_account
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
                movement_from.fromAccount = dest_account
                movement_from.value = -amount
                movement_from.description = description
                movement_from.save()
 
                movement_to = AccountMovement()
                movement_to.account = dest_account
                movement_to.fromAccount = from_account
                print(movement_from.fromAccount)
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

    amount = float(request.POST['loan_amount'])
    to_account = request.POST['to_account']

    number = random.randint(10000,99999)
    loan_account = f"LOAN_{to_account}{number}"

    customer = Customer.objects.get(user = request.user)

    account = Account()
    account.customer = customer
    account.accountNumber = loan_account
    account.isLoan = True
    account.save()

    account_movement = AccountMovement()
    account_movement.account = account
    account_movement.fromAccount = 'Bank'
    account_movement.value = -amount
    account_movement.description = "Loan"
    account_movement.save()

    loan = LoanRequest()
    loan.customer = customer
    loan.account = Account.objects.get(pk=pk)
    loan.loanAccount = Account.objects.get(accountNumber=loan_account)
    loan.loanAmount = amount
    loan.save()
 
    return HttpResponseRedirect(reverse('bank_app:index'))
 
 
@transaction.atomic
def accept_loan(request):

    if request.method == "POST":
        pk = request.POST['lpk']
        pkcust = request.POST['pk_cust']

        amount = float(request.POST['loan_amount'])

        to_account = request.POST['to_account']
        dest_account = Account.objects.filter(accountNumber=to_account)
        
        loan = LoanRequest.objects.get(pk=pk)
        loan_account = loan.loanAccount
 
        try:
            with transaction.atomic():          
                movement_to = AccountMovement()
                movement_to.account = dest_account[0]
                movement_to.fromAccount = 'Bank'
                movement_to.value = amount
                movement_to.description = 'Loan'
                movement_to.save()
 
                loan.loanAccount = loan_account
                loan.confirmed = 'true'
                loan.save()
 
        except IntegrityError:
            print('Transaction failed')
 
    return show_accounts(request, pkcust)
 
 
def decline_loan(request):
    pk = request.POST['lpk']
    pkcust = request.POST['pk_cust']
 
    loan = LoanRequest.objects.get(pk = pk)
    loan.confirmed = 'false'
    loan.save()
 
    return show_accounts(request, pkcust)
 
 
def del_loan(request):
    pk = request.POST['lpk']
    pkcust = request.POST['pk_cust']
    loan_acc_number = request.POST['loan_account']

    account = get_object_or_404(Account, accountNumber=loan_acc_number)
    account.delete()
 
    loan = get_object_or_404(LoanRequest, pk=pk)
    loan.delete()
   
    return show_accounts(request, pkcust)
 
 
def generate_card(request):
 
    pkcust = request.POST['pk']
    accountpk = request.POST['card_account']
 
    years = 5
    days_per_year = 365.24
 
    customer = get_object_or_404(Customer, pk=pkcust)
    account = get_object_or_404(Account, pk=accountpk)
    currency = account.currency

    card_number = random.randint(1000000000000000,9999999999999999)
    cvv = random.randint(100,999)

    card_balance = float(request.POST['initial_card_balance'])

    current_date = datetime.today()
    expiry_date = current_date + timedelta(days=(years*days_per_year))
 
    try:
        CreditCard.objects.get(cardNumber = card_number)
        print('Credit card number already exists')
 
    except:
        card = CreditCard()
        card.customer = customer
        card.account = account
        card.currency = currency
        card.cardNumber = card_number
        card.initialBalance = card_balance
        card.expiryDate = expiry_date
        card.cvvNumber = cvv
        card.save()
 
        card_movement = CardMovement()
        card_movement.card = card
        card_movement.value = 0
        card_movement.toFrom = 'Bank'
        card_movement.description = "Initial debt"
        card_movement.save()
 
    return show_accounts(request, pkcust)
 

def del_card(request):
    pk = request.POST['pk']
    pkcust = request.POST['pkcust']
 
    card = get_object_or_404(CreditCard, pk=pk)
    card.delete()
   
    return show_accounts(request, pkcust)
   
 
@transaction.atomic
def pay_debt(request):
    message = 'Success'
    is_error = False
 
    if request.method == "POST":
        pk = request.POST['pk']
        card = CreditCard.objects.get(pk=pk)

        from_accountpk = request.POST['from_account']
        from_account = Account.objects.get(pk=from_accountpk)
       
        amount = float(request.POST['card_repay'])
        remaining_amount = float(get_repay_amount_for_card(card))

        from_balance = get_balance_for_account(from_account)

        if amount <= 0 or amount > abs(remaining_amount):
            print('The amount you entered is not valid or exceeds the debt')
       
        elif from_balance > amount:
 
            try:
                with transaction.atomic():
                    movement_from = AccountMovement()
                    movement_from.account = from_account
                    movement_from.fromAccount = f"{card.cardNumber} (credit card)"
                    movement_from.value = -amount
                    movement_from.description = 'Credit card repay'
                    movement_from.save()
 
                    movement_to = CardMovement()
                    movement_to.card = card
                    movement_to.toFrom = from_account
                    movement_to.value = amount
                    movement_to.description = 'Credit card repay'
                    movement_to.save()
 
            except IntegrityError:
                message = 'Transaction  failed'
                is_error = True
                print('Transaction failed')
 
        else:
            print('Insufficient funds')
 
    return show_index(request, message, is_error)
 
 
@transaction.atomic
def pay_card(request):
    message = 'Success'
    is_error = False
 
    if request.method == "POST":
        from_cardpk = request.POST['card_pk']
        from_card = CreditCard.objects.get(pk=from_cardpk)

        to_account = request.POST['to_account']
        dest_account = Account.objects.get(accountNumber = to_account)

        balance = from_card.initialBalance
        amount = float(request.POST['card_pay'])
        description = request.POST['card_desc']
 
        if balance > amount:
            try:
                with transaction.atomic():
                    movement_from = CardMovement()
                    movement_from.card = from_card
                    movement_from.toFrom = dest_account
                    movement_from.value = -amount
                    movement_from.description = description
                    movement_from.save()
 
                    movement_from = AccountMovement()
                    movement_from.account = dest_account
                    movement_from.fromAccount = f"{from_card.cardNumber} (credit card)"
                    movement_from.value = amount
                    movement_from.description = description
                    movement_from.save()
 
            except IntegrityError:
                message = 'Transaction  failed'
                is_error = True
                print('Transaction failed')
 
        else:
            print('Insufficient funds')
 
    return show_index(request, message, is_error)
 

def add_interest():

    cards = CreditCard.objects.all()

    for c in cards.iterator():

        debt = get_repay_amount_for_card(c)

        if debt != 0:
            interest = (abs(debt)*15)/100

            c.interest = c.interest + interest
            c.save()
    return


@transaction.atomic
def charge_interest():

    cards = CreditCard.objects.all

    for c in cards.iterator():
        
        if c.interest > 0:
            try:
                with transaction.atomic():

                    movement = AccountMovement()
                    movement.account = c.acount
                    movement.fromAccount = 'Bank'
                    movement.value = -c.interest
                    movement.description = 'Credit card interest'
                    movement.save()
                    
                    c.interest = 0
                    c.save()

            except IntegrityError:
                print('Transaction failed')

    return


@transaction.atomic
def pay_interest2(request):
    pkcust = request.POST['pkcust']
    account_number = request.POST['to_account']
    card_number = request.POST['card_number']
    interest = float(request.POST['interest'])

    account = Account.objects.get(accountNumber=account_number)
    card = CreditCard.objects.get(cardNumber=card_number)

    try:
        with transaction.atomic():

            movement = AccountMovement()
            movement.account = account
            movement.fromAccount = 'Bank'
            movement.value = -interest
            movement.description = 'Credit card interest'
            movement.save()
            
            card.interest = 0
            card.save()

    except IntegrityError:
        print('Transaction failed')

    return show_accounts(request, pkcust)

  
def show_card_movements(request):
    context = {}
   
    pk = request.POST['pk']
 
    card = get_object_or_404(CreditCard, pk=pk)
    card_repay_balance = get_repay_amount_for_card(card)
    card_movements = CardMovement.objects.filter(card=card)
 
    context = {
            'usertype': get_user_type(request.user),
            'card': card,
            'card_repay_balance': card_repay_balance,
            'card_movements': card_movements,
    }
 
    return render(request, 'bank_app/card_movements.html', context)
