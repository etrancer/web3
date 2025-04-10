import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

SENDER = os.getenv("SENDER_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RECEIVER = os.getenv("RECEIVER_ADDRESS")

# RPC-провайдер
RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

assert w3.is_connected(), "❌ Не удалось подключиться к сети"

def get_balance(address):
    return w3.from_wei(w3.eth.get_balance(address), "ether")

def send_eth(amount_eth):
    nonce = w3.eth.get_transaction_count(SENDER)
    tx = {
        "type": 2,
        "nonce": nonce,
        "to": RECEIVER,
        "value": w3.to_wei(amount_eth, "ether"),
        "gas": 21000,
        "maxFeePerGas": w3.to_wei(3, "gwei"),
        "maxPriorityFeePerGas": w3.to_wei(1, "gwei"),
        "chainId": w3.eth.chain_id
    }
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash.hex()

# Вывод
print(f"🔗 Подключено к Sepolia, chain ID: {w3.eth.chain_id}")
print(f"💰 Баланс отправителя: {get_balance(SENDER)} ETH")
print(f"💰 Баланс получателя: {get_balance(RECEIVER)} ETH")

# Отправим 0.001 ETH
tx_hash = send_eth(0.001)
print(f"📤 TX отправлена: {tx_hash}")
