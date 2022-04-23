from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ExternalTransaction(APIView):
    def post(self, request, *args, **kwargs):
        
        to_account = request.data.get('to_account')
        print(to_account)

        
        return Response(
                    {"res": "OK"},
                    status=status.HTTP_200_OK
                )