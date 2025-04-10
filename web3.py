import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv
from datetime import datetime

# Загрузка переменных из .env
load_dotenv()
SENDER = os.getenv("SENDER_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RECEIVER = os.getenv("RECEIVER_ADDRESS")

# Подключение к сети Sepolia
RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

assert w3.is_connected(), "❌ Не удалось подключиться к сети Sepolia"

def eth(val_wei):
    return w3.from_wei(val_wei, "ether")

def get_balance(address):
    return eth(w3.eth.get_balance(address))

def get_nonce(address):
    return w3.eth.get_transaction_count(address)

def is_contract(address):
    return w3.eth.get_code(address) != b''

def get_transaction_info(tx_hash):
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    block = w3.eth.get_block(receipt.blockNumber)
    timestamp = datetime.utcfromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return {
        "status": receipt.status,
        "block": receipt.blockNumber,
        "gas_used": receipt.gasUsed,
        "timestamp": timestamp,
        "confirmations": w3.eth.block_number - receipt.blockNumber
    }

def get_latest_block_info():
    block = w3.eth.get_block('latest')
    return {
        "number": block.number,
        "timestamp": datetime.utcfromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
        "tx_count": len(block.transactions),
        "gas_limit": block.gasLimit,
        "base_fee": eth(block.baseFeePerGas) if 'baseFeePerGas' in block else None
    }

def estimate_gas(to_address, value_eth):
    txn = {
        'from': SENDER,
        'to': to_address,
        'value': w3.to_wei(value_eth, 'ether')
    }
    return w3.eth.estimate_gas(txn)

def send_eth(amount_eth):
    nonce = get_nonce(SENDER)
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

# === Вывод информации ===

print("✅ Подключено к Sepolia, Chain ID:", w3.eth.chain_id)
print("📦 Последний блок:", w3.eth.block_number)
print(f"💼 Отправитель: {SENDER}")
print(f"💰 Баланс отправителя: {get_balance(SENDER)} ETH")
print(f"💰 Баланс получателя: {get_balance(RECEIVER)} ETH")
print(f"🧾 Адрес получателя — {'контракт' if is_contract(RECEIVER) else 'пользователь'}")

# Отправка ETH
amount = 0.001
print(f"\n🚀 Отправка {amount} ETH → {RECEIVER}...")
tx_hash = send_eth(amount)
print(f"📤 TX отправлена: {tx_hash}")

# Подтверждение и детали транзакции
info = get_transaction_info(tx_hash)
print("\n📊 Информация о транзакции:")
for k, v in info.items():
    print(f"{k}: {v}")

# Последний блок
block_info = get_latest_block_info()
print("\n🧱 Последний блок:")
for k, v in block_info.items():
    print(f"{k}: {v}")

# Оценка газа
gas_est = estimate_gas(RECEIVER, 0.001)
print(f"\n⛽ Оценка газа для 0.001 ETH → {RECEIVER}: {gas_est} единиц")
