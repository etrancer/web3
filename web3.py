from web3 import Web3
from web3.middleware import geth_poa_middleware

# RPC‑endpoint Sepolia (на примере PublicNode):
RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"

# Подключение к сети
w3 = Web3(Web3.HTTPProvider(RPC_URL))
# Для сетей PoA вроде Sepolia нужно middleware:
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

assert w3.is_connected(), "Не удалось подключиться к Sepolia"

print("Chain ID‑сеть:", w3.eth.chain_id)  # должно быть 11155111

# Задайте свои адреса и приватный ключ
sender_address = "0xВашАдресОтправителя"
private_key = "0xВашПриватныйКлюч"
receiver = "0xАдресПолучателя"

# Проверяем балансы
def print_balances():
    print("Баланс отправителя:", w3.from_wei(w3.eth.get_balance(sender_address), "ether"), "ETH")
    print("Баланс получателя:", w3.from_wei(w3.eth.get_balance(receiver), "ether"), "ETH")

print_balances()

# Создаем EIP‑1559 транзакцию
nonce = w3.eth.get_transaction_count(sender_address)
tx = {
    "type": 2,
    "nonce": nonce,
    "maxFeePerGas": w3.to_wei(3, "gwei"),
    "maxPriorityFeePerGas": w3.to_wei(1, "gwei"),
    "gas": 21000,
    "to": receiver,
    "value": w3.to_wei(0.01, "ether"),
    "chainId": w3.eth.chain_id,
}

signed = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
print("Отправлена TX:", tx_hash.hex())

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Статус транзакции:", receipt.status)

print_balances()
