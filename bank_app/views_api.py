from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ExternalTransaction(APIView):
    def post(self, request, *args, **kwargs):
        print('Rest post')
        
        print(request.data)
        return Response(
                    {"res": "OK"},
                    status=status.HTTP_200_OK
                )