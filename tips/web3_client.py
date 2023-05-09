from web3 import Web3
import os


class SingletonMetaclass(type):
    _instance = None
    def __call__(cls, *args, **kwargs):
        assert not (args or kwargs), 'Singletone does not accept arguments'
        if isinstance(cls._instance, cls):
            return cls._instance
        else:
            cls._instance = super(SingletonMetaclass, cls).__call__()
            return cls._instance


class Web3Client(metaclass=SingletonMetaclass):
    def __init__(self):
        WEB3_INFURA_PROJECT_ID = os.environ.get('WEB3_INFURA_PROJECT_ID')
        CONTRACT = '0xD25bbC0E9F39D472af6F3f988C22f3481709Ed58'

        endpoint = f"https://sepolia.infura.io/v3/{WEB3_INFURA_PROJECT_ID}"
        self.w3 = Web3(Web3.HTTPProvider(endpoint))
        print('Web3 HTTPProvider initialized...')

        self.address = CONTRACT
        with open('tips/static/web3/abi.json', 'r') as f:
            self.abi = f.read()
        self.contract_instance = self.w3.eth.contract(address=self.address, abi=self.abi)
        print(f'Contract instance {self.address} initialized.')

    def create_account(self):
        acc = self.w3.eth.account.create()
        # self.w3.toHex(acc.private_key) <- do we need it?
        return acc.address

    def transfer(self, from_account, to_account, amount):
        self.contract_instance.functions.transferFrom(from_account, to_account, amount)
        return