import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv
import json

load_dotenv()

SENDER = os.getenv("SENDER_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
NFT_CONTRACT_ADDRESS = os.getenv("NFT_CONTRACT_ADDRESS")

# RPC подключение
RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

assert w3.is_connected(), "❌ Не удалось подключиться к сети"

# Стандартный минимальный ABI для ERC-721
erc721_abi = json.loads("""
[
  {"constant":true,"inputs":[{"name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"type":"function"},
  {"constant":true,"inputs":[{"name":"owner","type":"address"},{"name":"index","type":"uint256"}],"name":"tokenOfOwnerByIndex","outputs":[{"name":"","type":"uint256"}],"type":"function"},
  {"constant":true,"inputs":[{"name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"name":"","type":"string"}],"type":"function"},
  {"constant":false,"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"type":"function"}
]
""")

nft = w3.eth.contract(address=Web3.to_checksum_address(NFT_CONTRACT_ADDRESS), abi=erc721_abi)

def get_nft_balance(owner):
    return nft.functions.balanceOf(owner).call()

def get_token_id_by_index(owner, index):
    return nft.functions.tokenOfOwnerByIndex(owner, index).call()

def get_token_uri(token_id):
    return nft.functions.tokenURI(token_id).call()

def transfer_nft(token_id, to_address):
    nonce = w3.eth.get_transaction_count(SENDER)
    tx = nft.functions.safeTransferFrom(SENDER, to_address, token_id).build_transaction({
        "from": SENDER,
        "nonce": nonce,
        "gas": 150_000,
        "gasPrice": w3.to_wei(3, "gwei"),
        "chainId": w3.eth.chain_id
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash.hex()

# === Основной вывод ===
print(f"🔍 Проверка NFT для адреса {SENDER}")
balance = get_nft_balance(SENDER)
print(f"🎨 Количество NFT: {balance}")

if balance > 0:
    for i in range(balance):
        token_id = get_token_id_by_index(SENDER, i)
        token_uri = get_token_uri(token_id)
        print(f"🆔 Token #{token_id} URI: {token_uri}")
else:
    print("🙁 У вас нет NFT в этом контракте.")

# === Пример трансфера NFT ===
# receiver = "0xReceiverAddress"
# tx_hash = transfer_nft(token_id, receiver)
# print(f"📤 NFT #{token_id} отправлен → {receiver}, TX: {tx_hash}")

