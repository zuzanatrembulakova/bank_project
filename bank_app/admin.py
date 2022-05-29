from django.contrib import admin
from .models import Ranking, Currency, CurrencyRatio, Customer, Bank, AutomaticPayment, LoanRequest, Account, CreditCard


admin.site.register(Ranking)
admin.site.register(Currency)
admin.site.register(CurrencyRatio)
admin.site.register(Customer)
admin.site.register(Bank)
admin.site.register(AutomaticPayment)
admin.site.register(LoanRequest)
admin.site.register(Account)
admin.site.register(CreditCard)

# Register your models here.
