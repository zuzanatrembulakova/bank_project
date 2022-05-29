from locale import currency
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from .models import Account, AccountMovement, CurrencyRatio, Currency


class ExternalTransaction(APIView):
    def post(self, request, *args, **kwargs):
        
        to_account = request.data.get('to_account')
        from_account = request.data.get('from_account')
        from_currency_type = request.data.get('from_currency')
        amount = request.data.get('amount')
        description = request.data.get('description')

        bank_code = to_account[0:4]
        print(bank_code)

        account = Account.objects.get(accountNumber = to_account)
        from_currency = Currency.objects.get(type=from_currency_type)

        if not account:
            print('Account doesnt exist')
            res = 'Account doesnt exist'
            rec_code = status.HTTP_404_NOT_FOUND
    
        else:

            if from_currency != account.currency:
                currency_ratio = CurrencyRatio.objects.get(fromCurrency=from_currency, toCurrency=account.currency)
                amount = float(amount) * float(currency_ratio.ratio)

            account_movement = AccountMovement()
            account_movement.account = account
            account_movement.fromAccount = from_account
            account_movement.value = amount
            account_movement.description = description
            account_movement.save()

            res = 'Transaction successful'
            rec_code = status.HTTP_200_OK
        
        return Response(
                    {"res": res},
                    status=rec_code
                )


class CurrencyRatioView(APIView):
    def get(self, request, c1, c2, *args, **kwargs):

        try:
            from_currency = Currency.objects.get(type=c1)
            to_currency = Currency.objects.get(type=c2)

            currency = CurrencyRatio.objects.get(fromCurrency=from_currency, toCurrency=to_currency)
            
            return Response(
                        {"res": currency.ratio },
                        status=status.HTTP_200_OK
                    )

        except Exception:
            return Response(
                            {"res": "Not found" },
                            status=status.HTTP_404_NOT_FOUND
                        )


    def put(self, request, c1, c2, *args, **kwargs):

        try:
            from_currency = Currency.objects.get(type=c1)
            to_currency = Currency.objects.get(type=c2)

            currency = CurrencyRatio.objects.get(fromCurrency=from_currency, toCurrency=to_currency)
            
            currency.ratio = request.data.get('ratio')
            currency.save()

            return Response(
                        {"res": 'OK' },
                        status=status.HTTP_200_OK
                    )

        except Exception:
            return Response(
                            {"res": "Not found" },
                            status=status.HTTP_404_NOT_FOUND
                        )