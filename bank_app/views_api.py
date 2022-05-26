from email import message
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from .models import Account, AccountMovement

class ExternalTransaction(APIView):
    def post(self, request, *args, **kwargs):
        
        to_account = request.data.get('to_account')
        from_account = request.data.get('from_account')
        amount = request.data.get('amount')
        description = request.data.get('description')

        bank_code = to_account[0:4]
        print(bank_code)

        account = Account.objects.filter(accountNumber = to_account)

        if not account:
            print('Account doesnt exist')
            res = 'Account doesnt exist'
            rec_code = status.HTTP_404_NOT_FOUND
    
        else:

            account_movement = AccountMovement()
            account_movement.account = account[0]
            account_movement.fromAccount = from_account
            account_movement.value = amount
            account_movement.description = description
            account_movement.save()

            res = 'Transaction successful'
            rec_code = status.HTTP_200_OK
        
        return Response(
                    {"res": res },
                    status=rec_code
                )