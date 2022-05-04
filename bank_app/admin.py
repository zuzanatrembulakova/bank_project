from django.contrib import admin
from .models import Ranking, Customer, Bank, AutomaticPayment


admin.site.register(Ranking)
admin.site.register(Customer)
admin.site.register(Bank)
admin.site.register(AutomaticPayment)

# Register your models here.
