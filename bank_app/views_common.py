# views common functions

from .models import CreditCard, Customer, Account, AccountMovement, CardMovement
from django.contrib.auth.models import User
from django.db.models import Sum

def get_user_type(u:User) -> str:
    if u and u.is_authenticated:
        try:
            customer = Customer.objects.get(user = u)
            return "CUSTOMER"
        except:
            return "BANKER"
        return "unknown type"

def get_balance_for_account(acc:Account) -> int:
    result = AccountMovement.objects.filter(account = acc).aggregate(Sum('value'))
    return result['value__sum']

def get_repay_amount_for_card(card:CreditCard) -> int:
    result = CardMovement.objects.filter(card = card).aggregate(Sum('value'))
    return result['value__sum'] if result['value__sum'] != None else 0

