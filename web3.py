from web3 import Web3
from web3.middleware import geth_poa_middleware

# RPC-провайдер Sepolia (можно использовать Infura, Alchemy, PublicNode)
RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"

# Подключение
w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

assert w3.is_connected(), "❌ Не удалось подключиться к Sepolia"
print("✅ Подключение успешно")
print("Chain ID:", w3.eth.chain_id)
print("Последний номер блока:", w3.eth.block_number)

# Ваши данные
sender = "0xВашАдрес"
private_key = "0xВашПриватныйКлюч"
receiver = "0xАдресПолучателя"

# Проверка баланса
def get_balance(address):
    balance = w3.eth.get_balance(address)
    return w3.from_wei(balance, "ether")

print(f"\n💰 Баланс отправителя ({sender}): {get_balance(sender)} ETH")
print(f"💰 Баланс получателя ({receiver}): {get_balance(receiver)} ETH")

# Получить nonce (кол-во отправленных транзакций)
nonce = w3.eth.get_transaction_count(sender)
print(f"🔢 Nonce отправителя: {nonce}")

# Получить текущую цену газа
gas_price = w3.eth.gas_price
print(f"⛽ Текущая цена газа: {w3.from_wei(gas_price, 'gwei')} GWei")

# Проверка: по адресу контракт или обычный аккаунт?
code = w3.eth.get_code(receiver)
if code != b'':
    print(f"📦 {receiver} — контракт (длина кода: {len(code)} байт)")
else:
    print(f"👤 {receiver} — обычный EOА аккаунт")

# Создание и отправка транзакции
def send_eth(amount_eth):
    tx = {
        "type": 2,
        "nonce": w3.eth.get_transaction_count(sender),
        "to": receiver,
        "value": w3.to_wei(amount_eth, "ether"),
        "gas": 21000,
        "maxFeePerGas": w3.to_wei(3, "gwei"),
        "maxPriorityFeePerGas": w3.to_wei(1, "gwei"),
        "chainId": w3.eth.chain_id
    }
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"\n📤 Отправлена транзакция: {tx_hash.hex()}")
    return tx_hash.hex()

# Отправка 0.005 ETH
tx_hash = send_eth(0.005)

# Получить информацию о транзакции
def get_tx_info(tx_hash):
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"\n📦 Статус транзакции: {receipt.status} (1 = успех)")
    print(f"🔍 Блок: {receipt.blockNumber}")
    print(f"⏱️ Время включения: {w3.eth.get_block(receipt.blockNumber).timestamp}")
    print(f"📍 Газ использован: {receipt.gasUsed}")

get_tx_info(tx_hash)

# Повторный вывод балансов
print(f"\n✅ Баланс после транзакции:")
print(f"Отправитель: {get_balance(sender)} ETH")
print(f"Получатель: {get_balance(receiver)} ETH")
