from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import *
from .urls import *


class BankTestCase(TestCase):


    def setUp(self):
        Ranking.objects.create(rType='Gold', loan=True)
        Ranking.objects.create(rType='Silver', loan=True)
        Ranking.objects.create(rType='Basic', loan=False)

        gold = Ranking.objects.get(rType='Gold')
        silver = Ranking.objects.get(rType='Silver')
        basic = Ranking.objects.get(rType='Basic')

        user1 = Customer.objects.create(user=User.objects.create_user(
            'Adela Banasova', '', 'adela123'
        ), phone=12345678, ranking=gold)
        user2 = Customer.objects.create(user=User.objects.create_user(
            'Bob Pancakes', '', 'bob123'
        ), phone=87654321, ranking=silver)

        acc1 = Account.objects.create(customer=user1, accountNumber='acc1')
        acc2 = Account.objects.create(customer=user2, accountNumber='acc2')


    def test_create_customer(self):
        c = Client()

        data = {
            'name': 'Nancy Landgraab',
            'password': 'nancy123',
            'phone': 99885529, 
        }

        c.post(reverse('bank_app:create_customer'), data, follow=True)
        self.assertTrue(Customer.objects.get(phone='99885529'))

    
    def test_update_ranking(self):
        c = Client()

        user = Customer.objects.get(phone=12345678)
        basic = Ranking.objects.get(rType='Basic')

        data = {
            'pk': user.pk,
            'ranking': basic.pk
        }

        c.post(reverse('bank_app:update_ranking'), data, follow=True)
        
        user = Customer.objects.get(phone=12345678)
                
        self.assertEqual(user.ranking, basic)


    def test_add_account(self):
        c = Client()

        user = Customer.objects.get(phone=12345678)

        data = {
            'pk': user.pk,
            'number': 'textAccountNumber',
            'balance': 1000,
        }

        c.post(reverse('bank_app:add_account'), data, follow=True)
        self.assertTrue(Account.objects.get(accountNumber='textAccountNumber'))

    
    def test_set_transaction(self):
        c = Client()

        user1 = Customer.objects.get(phone=12345678)
        acc1 = Account.objects.get(customer=user1)
        accmv1 = AccountMovement.objects.create(account=acc1, value=1000, description='Initial balance')

        user2 = Customer.objects.get(phone=87654321)
        acc2 = Account.objects.get(customer=user2)
        accmv2 = AccountMovement.objects.create(account=acc2, value=1000, description='Initial balance')

        data = {
            'from_account': acc1.pk,
            'amount': '100',
            'description': 'Test transaction',
            'to_account': acc2.accountNumber,
            'payment_check': True,
            'repeat_number': 5,
            'repeat_time_unit': 'minute',
            'repeat_every': 2,
        }

        c.post(reverse('bank_app:set_transaction'), data, follow=True)
        accmv1 = AccountMovement.objects.filter(account=acc1)
        accmv2 = AccountMovement.objects.filter(account=acc2)
        self.assertTrue(accmv1[0].value + accmv1[1].value == 900)
        self.assertTrue(accmv2[0].value + accmv2[1].value == 1100)

    
    def test_request_loan(self):
        c = Client()

        user = Customer.objects.get(phone=12345678)
        acc = Account.objects.get(customer=user)

        c.login(username='Adela Banasova', password='adela123')

        data = {
            'pk': acc.pk,
            'loan_amount': '1000',
        }

        c.post(reverse('bank_app:request_loan'), data, follow=True)
        self.assertTrue(Loan.objects.get(account=acc))


    def test_accept_loan(self):
        c = Client()

        user = Customer.objects.get(phone=12345678)
        acc = Account.objects.get(customer=user)
        loan = Loan.objects.create(customer=user, account=acc, loanAmount=1000, remainingAmount=1000)

        data = {
            'pk': loan.pk,
            'pkcust': user.pk,
            'loan_amount': 100,
            'to_account': acc.accountNumber,
        }

        c.post(reverse('bank_app:accept_loan'), data, follow=True)
        loan = Loan.objects.get(pk=loan.pk)
        self.assertTrue(loan.confirmed == 'true')


    def test_decline_loan(self):
        c = Client()

        user = Customer.objects.get(phone=12345678)
        acc = Account.objects.get(customer=user)
        loan = Loan.objects.create(customer=user, account=acc, loanAmount=1000, remainingAmount=1000)

        data = {
            'pk': loan.pk,
            'pkcust': user.pk,
        }

        c.post(reverse('bank_app:decline_loan'), data, follow=True)
        loan = Loan.objects.get(pk=loan.pk)
        self.assertTrue(loan.confirmed == 'false')

    
    def test_pay_loan(self):
        c = Client()

        user = Customer.objects.get(phone=12345678)
        acc = Account.objects.get(customer=user)
        accmv = AccountMovement.objects.create(account=acc, value=1000, description='Initial balance')
        loan = Loan.objects.create(customer=user, account=acc, loanAmount=1000, remainingAmount=1000)

        data = {
            'pk': loan.pk,
            'account': acc,
            'remaining_amount': loan.remainingAmount,
            'loan_transfer': 500,
        }

        c.post(reverse('bank_app:pay_loan'), data, follow=True)
        loan = Loan.objects.get(pk=loan.pk)
        self.assertTrue(loan.remainingAmount == 500)

