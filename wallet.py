# Importing libraries
import subprocess
import json
import os

from constants import BTC, BTCTEST, ETH
from dotenv import load_dotenv
load_dotenv()

from bit import Key, PrivateKey, PrivateKeyTestnet
from bit.network import NetworkAPI

from web3 import Web3, middleware, Account

# Connecting Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1.8545"))
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware

# enable PoA middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Setting gas price strategy to medium algorithm
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

# Generating a Mnemonic using https://iancoleman.io/bip39/
# Set this mnemonic as an environment variable, and include the one you generated as a fallback
mnemonic = os.getenv('MNEMONIC')
#move pitch crowd athlete twist toe silly shoot simple later shaft ready

# Deriving the wallet keys
# 1st function. Calling the php file.
def derive_wallets(coin=BTC, mnemonic=mnemonic, depth=3):
    command = f'php ./derive -g --mnemonic="{mnemonic}" --cols=all --coin={coin} --numderive={depth} --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    return json.loads(output)

# Linking the transaction signing libraries
# Now, we need to use bit and web3.py to leverage the keys we've got in the coins object.
# You will need to create three more functions: priv_keys_to_account, create_tx, send_tx

# 2nd function. Convert private key string.
def priv_key_to_account(coin, priv_key):
    # convert the privkey string in a child key to an account object that bit or web3.py can use to transact.
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    # This is a function from the bit libarary that converts the private key string into a WIF (Wallet Import Format) object.
    # WIF is a special format bitcoin uses to designate the types of keys it generates. https://ofek.dev/bit/dev/api.html
    
#eth_acc = priv_key_to_account(ETH,eth_PrivateKey)
#btc_acc = priv_key_to_account(BTCTEST,btc_PrivateKey)

# 3rd function. Creating the raw, unsigned transaction that contains all meradata needed to transact.
def create_tx(coin, account, to, amount):
    if coin == ETH:
        value = w3.toWei(amount, "ether")
        gasEstimate = w3.eth.estimateGas({"from": account.address, "to": to, "amount": value})
        return {
            "to": to,
            "from": account.address,
            "value": value,
            "gas": gasEstimate,
            "gasPrice": w3.eth.generateGasPrice(),
            "nonce": w3.eth.getTransactionCount(account.address),
            "chainId": w3.net.chainId
        }
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

# 4th fucntion. Creating the transactions, signing, sending to designated network.
def send_tx(coin, account, to, amount):
    if coin == ETH:
        raw_tx = create_tx(coin, account, to, amount)
        signed = account.signTransaction(raw_tx)
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    if coin == BTCTEST:
        raw_tx = create_tx(coin, account, to, amount)
        signed = account.signTransaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed)

# Creating an object called coins that derives ETH and BTCTEST wallets with this function.
coins = {
    ETH: derive_wallets(coin=ETH),
    BTCTEST: derive_wallets(coin=BTCTEST),
}

# You should now be able to select child accounts (and thus, private keys) by calling coins[COINTYPE][INDEX]['privkey']. 

# Local PoA Ethereum transaction
# Add one of the ETH addresses to the pre-allocated accounts in your networkname.json.
# In this case, my testnet ETH addresses are
# 0x374d85Ade40CB31F09cAF7bfb051153ba28B6C86 AND
# 0xE4BDb0045554fce80525f67E4268EFE034c6BA20