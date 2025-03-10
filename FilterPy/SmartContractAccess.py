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

# Transaction Call
def send_transaction():
    account = w3.eth.accounts[0] 
    transaction = contract.functions.setValue(42).buildTransaction({
        'chainId': 1337, 
        'gas': 2000000,
        'gasPrice': w3.toWei('20', 'gwei'),
        'nonce': w3.eth.getTransactionCount(account),
    })

    signed_txn = w3.eth.account.signTransaction(transaction, private_key)

    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f"Transaction sent with hash: {txn_hash.hex()}")


call_contract_method()
# send_transaction() 
