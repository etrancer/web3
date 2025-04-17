import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv
import json
from decimal import Decimal

load_dotenv()

w3 = Web3(Web3.HTTPProvider("https://ethereum-sepolia-rpc.publicnode.com"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

assert w3.is_connected(), "RPC не отвечает"

# === ENV ===
FACTORY = Web3.to_checksum_address(os.getenv("FACTORY_ADDRESS"))
WETH = Web3.to_checksum_address(os.getenv("WETH_ADDRESS"))
DAI = Web3.to_checksum_address(os.getenv("DAI_ADDRESS"))
FEE = 3000  # 0.3% pool

# === ABIs ===
with open("abis/uniswap_factory_abi.json") as f:
    factory_abi = json.load(f)
with open("abis/uniswap_pool_abi.json") as f:
    pool_abi = json.load(f)
with open("abis/erc20_abi.json") as f:
    erc20_abi = json.load(f)

factory = w3.eth.contract(address=FACTORY, abi=factory_abi)

# === Получаем адрес пула ===
pool_address = factory.functions.getPool(WETH, DAI, FEE).call()
if pool_address == "0x0000000000000000000000000000000000000000":
    print("❌ Пул не найден.")
    exit()

print(f"✅ Адрес пула: {pool_address}")
pool = w3.eth.contract(address=pool_address, abi=pool_abi)

# === Чтение состояния пула ===
slot0 = pool.functions.slot0().call()
sqrtPriceX96 = slot0[0]
tick = slot0[1]
liquidity = pool.functions.liquidity().call()
token0 = pool.functions.token0().call()
token1 = pool.functions.token1().call()

print(f"📊 sqrtPriceX96: {sqrtPriceX96}")
print(f"📈 Tick: {tick}")
print(f"💧 Liquidity: {liquidity}")
print(f"🔗 Token0: {token0}")
print(f"🔗 Token1: {token1}")

# === Вычисляем цену ===
def price_from_sqrtX96(sqrt_price_x96):
    return Decimal(sqrt_price_x96) ** 2 / (2 ** 192)

price = price_from_sqrtX96(sqrtPriceX96)
print(f"💱 Цена (token1/token0): {price:.6f}")

