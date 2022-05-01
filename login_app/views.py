import re
from django.shortcuts import render, reverse
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect
from bank_app.views_common import *
from bank_app.models import *
from .models import *
from twilio.rest import Client
import random

from login_app.models import LoginCode

def login(request):
    context = {}
    verified = 0

    if request.method == "POST":
        user = authenticate(request, username=request.POST['name'], password=request.POST['password'])
        userType = get_user_type(user)    
        if user:
            dj_login(request, user)

            customer = Customer.objects.get(user = request.user) 
            print(customer.phone)

            sms_code = random.randint(1000,9999)
            code = LoginCode()
            code.code = sms_code
            code.save()
            print(code)

            # client = Client('AC19cbcef853566442dffb9784e745034d','147803e3c78223a9280f4d5b6953c1f1')
            # message = client.messages.create(
            #     body=f'Here is your code: {code}',
            #     from_='+19707167454',
            #     to='+4571803342'
            #     to=customer.phone
            # )
            # print(message.body) 

            # if (int(request.POST['sms_code']) == "") and (int(request.POST['sms_code']) == code)

            context = {                                                                             
                'verified': verified,
                'code': code
                }

            print(f"Logged in as {userType}")
            # return render(request, 'login_app/login.html', context)
            # return login_verify(request, login_step, code)
            # return HttpResponseRedirect(reverse('bank_app:index'))
        else:
            print('Invalid Login')
            context = {                                                                             
                'error': 'Bad username or password.'
                }
    return render(request, 'login_app/login.html', context)


def login_verify(request):
    context = {}
    user_code = request.POST['code']
    codepk = request.POST['codepk']
    code = LoginCode.objects.get(pk = codepk)

    if user_code == code:
        code.delete()
        # context = {                                                                             
        #     'login_step': login_step
        #     }
        return HttpResponseRedirect(reverse('bank_app:index'))
    else:
        verify_error = 'Wrong code' 
        context = {              
            'verify_error': verify_error,
            }

    return HttpResponseRedirect(reverse('bank_app:index'))


def logout(request):
    dj_logout(request)
    return render(request, 'login_app/login.html')
