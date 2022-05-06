from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Customer, Ranking
from .urls import *


class BankTestCase(TestCase):

    def setUp(self):
        Ranking.objects.create(rType='Gold', loan=True)
        Ranking.objects.create(rType='Silver', loan=True)
        Ranking.objects.create(rType='Basic', loan=False)

        gold = Ranking.objects.get(rType='Gold')
        silver = Ranking.objects.get(rType='Silver')
        basic = Ranking.objects.get(rType='Basic')

        Customer.objects.create(user=User.objects.create_user(
            'Adela Banasova', '', 'adela123'
        ), phone=12345678, ranking=gold)
        Customer.objects.create(user=User.objects.create_user(
            'Bob Pancakes', '', 'bob123'
        ), phone=87654321, ranking=silver)
    
    def test_update_ranking(self):
        c = Client()

        user1 = Customer.objects.get(phone=12345678)
        basic = Ranking.objects.get(rType='Basic')

        data = {
            'pk': user1.pk,
            'ranking': 'Basic'
        }

        result = c.post(reverse('bank_app:update_ranking'), data, follow=True)
        print('Result', result.status_code)
        print('User', user1.ranking)
        print('Basic', basic)
        self.assertEqual(user1.ranking, basic)
        # assert user1.ranking == basic