from django.contrib import admin
from .models import Ranking, Currency, CurrencyRatio, Customer, Bank, AutomaticPayment


admin.site.register(Ranking)
admin.site.register(Currency)
admin.site.register(CurrencyRatio)
admin.site.register(Customer)
admin.site.register(Bank)
admin.site.register(AutomaticPayment)

# Register your models here.
