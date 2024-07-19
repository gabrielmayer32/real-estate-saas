# In exchange_rates/management/commands/fetch_exchange_rates.py
import requests
from django.core.management.base import BaseCommand
from properties.models import ExchangeRate

class Command(BaseCommand):
    help = 'Fetch and update exchange rates'

    def handle(self, *args, **kwargs):
        response = requests.get('https://api.exchangerate-api.com/v4/latest/MUR')  # Use any reliable exchange rate API
        data = response.json()

        rates = data['rates']
        for currency, rate in rates.items():
            ExchangeRate.objects.update_or_create(currency=currency, defaults={'rate': rate})

        self.stdout.write(self.style.SUCCESS('Successfully updated exchange rates'))
