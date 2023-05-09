from django.apps import AppConfig
from .web3_client import Web3Client


class TipsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tips'

    def ready(self):
        Web3Client()
