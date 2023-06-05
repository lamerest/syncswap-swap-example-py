from web3 import Web3 
import web3
import json
from eth_abi import encode
import time
import math

zero_address = '0x0000000000000000000000000000000000000000'

endpoint_uri = 'https://mainnet.era.zksync.io'
w3 = Web3(Web3.HTTPProvider(endpoint_uri))

caller = '0x0F4da9EB1c529f681ddC9d7eBAd4FB728ed33536'
print('Balance', w3.eth.get_balance(caller)/ 10e18)

nonce = w3.eth.get_transaction_count(caller)
print('nonce', nonce)


# ETH = wETH - wETH is used internally
weth_addr = '0x5aea5775959fbc2557cc8789bc1bf90a239d9a91'
# USDC
usdc_addr = '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'

pool_addr = '0x80115c708E12eDd42E504c1cD52Aea96C547c05c'

router_addr = '0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295'

# Getting ABIs
router_abi_file = open('./router-abi.json')
router_abi = json.load(router_abi_file)

pool_abi_file = open('./pool-abi.json')
pool_abi = json.load(pool_abi_file)

# Getting reserves from pool contract
pool = w3.eth.contract(address=pool_addr, abi=pool_abi)
print(pool)
reserves = pool.functions.getReserves().call()
print(reserves)

[reserves_usdc, reserves_eth] = reserves
print('eth reserves', reserves_eth / 10e18)
print('usdc reserves', reserves_usdc / 10e5)

# Build swapData
amount = 100000000000000 # 0.0001 ETH

withdraw_mode = 1 # 1 - returns ETH, 2 - returns wETH

swapData = encode(['address', 'address', 'uint8'], [weth_addr, usdc_addr, withdraw_mode])

# Build steps
steps = [
    {
        'pool': pool_addr,
        'data': swapData,
        'callback': zero_address,
        'callbackData': '0x'
	}
]

print(steps)


# Build paths
native_eth_address = zero_address

paths = [
    {
        'steps': steps,
        'tokenIn': native_eth_address,
        'amountIn': amount
	}
]

print(paths)

# Call swap()
router = w3.eth.contract(address=router_addr, abi=router_abi)

print(router)

amountOutMin = 0
deadline = math.floor(time.time() + 60 * 30)
print('Deadline', deadline) # 30 minutes

# Call static
tx = router.functions.swap(paths, amountOutMin,  deadline).call({ "from": caller, "nonce": nonce, "value": amount })
print(tx)