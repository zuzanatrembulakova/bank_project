from email import message
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from .models import Account, AccountMovement

class ExternalTransaction(APIView):
    def post(self, request, *args, **kwargs):
        
        to_account = request.data.get('to_account')
        amount = request.data.get('amount')
        description = request.data.get('description')

        bank_code = to_account[0:4]
        print(bank_code)

        if not Account.objects.filter(accountNumber = to_account):
            print('Account doesnt exist')
            res = 'Account doesnt exist'
            return Response(
                    {"res": res},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:

            account = get_object_or_404(Account, accountNumber = to_account)
            print(account)

            account_movement = AccountMovement()
            account_movement.account = account
            account_movement.value = amount
            account_movement.description = description
            account_movement.save()

            res = 'Transaction successful'
        
        return Response(
                    {"res": res },
                    status=status.HTTP_200_OK
                )