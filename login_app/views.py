from django.shortcuts import render, reverse
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect
from bank_app.views_common import *
from bank_app.models import *


def login(request):
    context = {}
    if request.method == "POST":
        user = authenticate(request, username=request.POST['name'], password=request.POST['password'])
        userType = get_user_type(user)       
        if user:
            dj_login(request, user)

            # client = Client('AC19cbcef853566442dffb9784e745034d','147803e3c78223a9280f4d5b6953c1f1')
            # message = client.messages.create(
            #     body='Test message',
            #     from_='+19707167454',
            #     to='+4571803342'
            # )
            # print(message.body) 

            print(f"Looged in as {userType}")
            return HttpResponseRedirect(reverse('bank_app:index'))
        else:
            print('Invalid Login')
            context = {                                                                             
                'error': 'Bad username or password.'
                }
    return render(request, 'login_app/login.html', context)

def logout(request):
    dj_logout(request)
    return render(request, 'login_app/login.html')
