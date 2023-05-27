from web3 import Web3
from web3.exceptions import TimeExhausted
from web3.middleware import construct_sign_and_send_raw_middleware
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
        if WEB3_INFURA_PROJECT_ID is None:
            print("Infura API key is empty!")

        endpoint = f"https://sepolia.infura.io/v3/{WEB3_INFURA_PROJECT_ID}"
        self.w3 = Web3(Web3.HTTPProvider(endpoint))
        print('Web3 HTTPProvider initialized...')

        deployment_account_pk = os.environ.get('DEPLOYMENT_ACCOUNT_PK')
        if deployment_account_pk is None:
            print("Deployment account not set!")
        self.deployment_account = self.w3.eth.account.from_key(deployment_account_pk)
        # add middleware to sign with deployment_account PK under the hood
        self.w3.middleware_onion.add(construct_sign_and_send_raw_middleware(self.deployment_account))

        CONTRACT = '0xD25bbC0E9F39D472af6F3f988C22f3481709Ed58'
        self.address = CONTRACT
        with open('tips/static/web3/abi.json', 'r') as f:
            self.abi = f.read()
        self.pekoe = self.w3.eth.contract(address=self.address, abi=self.abi)
        print(f'Contract instance {self.address} initialized.')

    # balance of deployment_account
    def balance(self):
        return self.pekoe.functions.balanceOf(self.deployment_account.address).call()

    def balance_of(self, account):
        return self.pekoe.functions.balanceOf(account).call()

    # simulate buying of the tokens
    def buy(self, account, amount):
        print(f"Buying {amount} PEKOE tokens for {account}...")
        tx_hash = self.pekoe.functions.transfer(account, amount).transact({
            'from': self.deployment_account.address
            })
        try:
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        except TimeExhausted:
            print(f"Transaction {tx_hash} took to long to be added to the block.")
            return False
        print(tx_receipt)
        print(f"{amount} PEKOE tokens for {account} bought.")
        return True

    # transfer ETH to the account to pay gas fees
    def _transfer_fee(self, account, eth):
        print(f"Transferring {eth} ETH for gas fees to account {account}...")
        tx_hash = self.w3.eth.send_transaction({
            'from': self.deployment_account.address,
            'to': account,
            'value': eth
        })
        try:
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        except TimeExhausted:
            print(f"Transaction {tx_hash} took to long to be added to the block.")
        print(tx_receipt)
        print(f'{eth} ETH for gas fee to {account} transferred.')
        return True

    # approve usage(transferFrom/burnFrom) for amount of tokens of account for deployment_account
    def _approve_allowance(self, account, amount, pk_env):
        # check allowance
        cur_allowance = self.pekoe.functions.allowance(account, self.deployment_account.address).call()
        if cur_allowance < amount:
            print(f"Approving retrieval of {amount} PEKOE tokens from {account} for {self.deployment_account.address}...")
            # should approve first
            unsent_approve_tx = self.pekoe.functions.approve(self.deployment_account.address,
                                                             amount - cur_allowance).build_transaction(
                {'from': account, 'nonce': self.w3.eth.get_transaction_count(account)})
            self._transfer_fee(account, unsent_approve_tx['maxFeePerGas'] * unsent_approve_tx['gas'])
            signed_approve_tx = self.w3.eth.account.sign_transaction(unsent_approve_tx,
                                                                     private_key=os.environ.get(pk_env))
            approve_tx_hash = self.w3.eth.send_raw_transaction(signed_approve_tx.rawTransaction)
            try:
                approve_tx_receipt = self.w3.eth.wait_for_transaction_receipt(approve_tx_hash)
            except TimeExhausted:
                print(f"Transaction {approve_tx_hash} took to long to be added to the block.")
                return False
            print(approve_tx_receipt)
            assert self.pekoe.functions.allowance(account, self.deployment_account.address).call() == amount
            print("Approval successful.")
        return True

    def transfer(self, from_account, to_account, amount, pk_env):
        approval_res = self._approve_allowance(from_account, amount, pk_env)
        if not approval_res:
            return False
        print(f'Transferring {amount} PEKOE tokens from customer {from_account} to waiter {to_account}...')
        tx_hash = self.pekoe.functions.transferFrom(from_account, to_account,
                                                    amount).transact({'from': self.deployment_account.address})
        try:
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        except TimeExhausted:
            print(f"Transaction {tx_hash} took to long to be added to the block.")
            return False
        print(tx_receipt)
        print(f'Transferred {amount} PEKOE tokens from customer {from_account} to waiter {to_account}.')
        return tx_receipt["status"] == 1

    def _mint(self, amount):
        print(f"Deployment account balance: {self.balance()}")
        print(f"Minting {amount} PEKOE tokens after burning...")
        tx_hash = self.pekoe.functions.mint(self.deployment_account.address,
                                            amount).transact({'from': self.deployment_account.address})
        try:
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        except TimeExhausted:
            print(f"Transaction {tx_hash} took to long to be added to the block.")
            return False
        print(tx_receipt)
        print(f"Minted {amount} PEKOE tokens.")
        print(f"Deployment account balance: {self.balance()}")
        return True

    def _burn(self, account, amount, pk_env):
        approval_res = self._approve_allowance(account, amount, pk_env)
        if not approval_res:
            return False
        print(f"Burning {amount} PEKOE tokens from {account}...")
        tx_hash = self.pekoe.functions.burnFrom(account, amount).transact({'from': self.deployment_account.address})
        try:
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        except TimeExhausted:
            print(f"Transaction {tx_hash} took to long to be added to the block.")
            return False
        print(tx_receipt)
        print(f"Burned {amount} PEKOE tokens from {account}")
        return True

    # simulate exchanging tokens for fiat
    def exchange_fiat(self, account, amount, pk_env):
        res = self._burn(account, amount, pk_env)
        if not res:
            return False
        res = self._mint(amount)
        if not res:
            return False
        return True
