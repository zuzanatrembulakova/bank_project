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

        Account.objects.create(customer=user1, accountNumber='acc1')
        Account.objects.create(customer=user2, accountNumber='acc2')


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
