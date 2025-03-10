import sys
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

if not w3.is_connected():
    print("Connection failed!")
    exit()

if len(sys.argv) < 3:
    print("Usage: python SmartContractAccess.py <contract_address> <private_key>")
    sys.exit(1)

contract_address = sys.argv[1] 
private_key = sys.argv[2]


contract_abi = [
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_value",
				"type": "uint256"
			}
		],
		"name": "setValue",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getValue",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Read Only Method
def call_contract_method():
    try:
        result = contract.functions.getValue().call()
        print(f"Result from contract method: {result}")
    except Exception as e:
        print(f"Error calling method: {e}")

# Transaction Call (Write)
def send_transaction():
    account = w3.eth.accounts[0] 
    transaction = contract.functions.setValue(42).build_transaction({
        'chainId': 1337, 
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(account),
    })

    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

    txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Transaction sent with hash: {txn_hash.hex()}")

print("=== Reading Values ===")
call_contract_method()
print("=== Running Filter ===")
send_transaction() 
print("=== Safety Check ===")
call_contract_method()