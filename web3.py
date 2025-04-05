from web3 import Web3

# Подключаемся к Ganache (RPC по умолчанию — порт 8545)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

assert w3.is_connected(), "Не удалось подключиться к Ganache"

# Доступные аккаунты
accounts = w3.eth.accounts
sender = accounts[0]
receiver = accounts[1]

print("Баланс send до:", w3.from_wei(w3.eth.get_balance(sender), "ether"), "ETH")

# Перевод 0.5 ETH
tx = {
    'from': sender,
    'to': receiver,
    'value': w3.to_wei(0.5, "ether"),
    'gas': 21000,
}
tx_hash = w3.eth.send_transaction(tx)
w3.eth.wait_for_transaction_receipt(tx_hash)

print("Баланс send после:", w3.from_wei(w3.eth.get_balance(sender), "ether"), "ETH")
print("Баланс recv после:", w3.from_wei(w3.eth.get_balance(receiver), "ether"), "ETH")

