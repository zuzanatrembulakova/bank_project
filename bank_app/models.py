from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Ranking(models.Model):
    rType = models.CharField(max_length=200)
    loan = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.rType} - {self.loan}"


class Currency(models.Model):
    type = models.CharField(max_length=200, default='DKK')
    name = models.CharField(max_length=200, default='Danish Krone')

    def __str__(self):
        return f"{self.type}"


class CurrencyRatio(models.Model):
    fromCurrency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='fromCurrency')
    toCurrency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    ratio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.fromCurrency} - {self.toCurrency} - {self.ratio}"


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.IntegerField()
    ranking = models.ForeignKey(Ranking, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.phone}"


class Account(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, default=1)
    accountNumber = models.CharField(max_length=20)
    isLoan = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.accountNumber}"


class AccountMovement(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    fromAccount = models.CharField(max_length=20, default='undefined')
    value = models.DecimalField(max_digits=30, decimal_places=2)
    timestamp = models.DateTimeField(default=now, editable=False)
    description = models.TextField()

    def __str__(self):
        return f"{self.value} - {self.timestamp} - {self.description}"


class Bank(models.Model):
    bankCode = models.CharField(max_length=4)
    path = models.CharField(max_length=250)
    
    def __str__(self):
        return f"{self.bankCode} - {self.path}"


class LoanRequest(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    loanAccount = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='loanAccount')
    loanAmount = models.DecimalField(max_digits=30, decimal_places=2)
    confirmed = models.CharField(max_length=100, default='undefined')

    def __str__(self):
        return f"{self.account} - {self.loanAmount} - {self.loanAccount} - {self.confirmed}"


class AutomaticPayment(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    toAccount = models.CharField(max_length=250, default='undefined')
    value = models.DecimalField(max_digits=30, decimal_places=2)
    description = models.TextField()
    repeatNumber = models.IntegerField(help_text="number of payment repeats")
    repeatEvery = models.IntegerField(help_text="how often should we repeat payment (in minutes)")
    timestamp = models.DateTimeField(default=now, editable=False, help_text="time of last payment")

    def __str__(self):
        return f"{self.account} - {self.toAccount} - {self.value} - {self.repeatNumber} - {self.timestamp}"


class CreditCard(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    cardNumber = models.IntegerField()
    initialBalance = models.DecimalField(max_digits=30, decimal_places=2)
    expiryDate = models.DateField(editable=False)
    cvvNumber = models.IntegerField()
    interest = models.DecimalField(max_digits=30, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.account.accountNumber} - {self.cardNumber} - {self.initialBalance} - {self.expiryDate} - {self.interest}"
        

class CardMovement(models.Model):
    card = models.ForeignKey(CreditCard, on_delete=models.CASCADE)
    toFrom = models.CharField(max_length=20, default='undefined')
    value = models.DecimalField(max_digits=30, decimal_places=2)
    timestamp = models.DateTimeField(default=now, editable=False)
    description = models.TextField()

    def __str__(self):
        return f"{self.value} - {self.timestamp} - {self.description}"
