import os
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv

load_dotenv()

# ENV
SENDER = os.getenv("SENDER_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ROUTER = Web3.to_checksum_address(os.getenv("UNISWAP_ROUTER"))
WETH = Web3.to_checksum_address(os.getenv("WETH_ADDRESS"))
DAI = Web3.to_checksum_address(os.getenv("DAI_ADDRESS"))

RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

assert w3.is_connected(), "❌ RPC не отвечает"

# ABIs
with open("abis/uniswap_router_abi.json") as f:
    router_abi = json.load(f)
with open("abis/erc20_abi.json") as f:
    erc20_abi = json.load(f)

router = w3.eth.contract(address=ROUTER, abi=router_abi)

def get_token_contract(address):
    return w3.eth.contract(address=Web3.to_checksum_address(address), abi=erc20_abi)

def approve_if_needed(token, amount, spender):
    allowance = token.functions.allowance(SENDER, spender).call()
    if allowance >= amount:
        return
    tx = token.functions.approve(spender, amount).build_transaction({
        "from": SENDER,
        "nonce": w3.eth.get_transaction_count(SENDER),
        "gas": 100_000,
        "gasPrice": w3.to_wei(3, "gwei"),
        "chainId": w3.eth.chain_id
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"✅ Approve отправлен: {tx_hash.hex()}")
    w3.eth.wait_for_transaction_receipt(tx_hash)

def swap_tokens(token_in, token_out, amount_in_eth, is_eth_in=False):
    deadline = w3.eth.get_block('latest').timestamp + 300
    amount_in = w3.to_wei(amount_in_eth, 'ether')
    amount_out_min = int(amount_in * 0.95)

    if not is_eth_in:
        token_contract = get_token_contract(token_in)
        approve_if_needed(token_contract, amount_in, ROUTER)

    params = {
        "tokenIn": token_in,
        "tokenOut": token_out,
        "fee": 3000,
        "recipient": SENDER,
        "deadline": deadline,
        "amountIn": amount_in,
        "amountOutMinimum": amount_out_min,
        "sqrtPriceLimitX96": 0
    }

    tx_data = router.functions.exactInputSingle(params).build_transaction({
        "from": SENDER,
        "value": amount_in if is_eth_in else 0,
        "gas": 300000,
        "gasPrice": w3.to_wei(3, "gwei"),
        "nonce": w3.eth.get_transaction_count(SENDER),
        "chainId": w3.eth.chain_id
    })

    signed = w3.eth.account.sign_transaction(tx_data, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"📤 Swap TX отправлен: {tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("✅ Swap завершен, статус:", receipt.status)

# === ИСПОЛЬЗОВАНИЕ ===
# Варианты:
# ETH → DAI
swap_tokens(WETH, DAI, 0.01, is_eth_in=True)

# DAI → ETH
# swap_tokens(DAI, WETH, 0.01, is_eth_in=False)

# DAI → USDC (если есть)
# swap_tokens(DAI, USDC, 0.01, is_eth_in=False)
