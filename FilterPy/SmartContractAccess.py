import sys
import time
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
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "_addr",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "value",
				"type": "uint256"
			}
		],
		"name": "IncomingRequest",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "_addr",
				"type": "address"
			}
		],
		"name": "RequestFail",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "_addr",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "value",
				"type": "uint256"
			}
		],
		"name": "RequestSuccess",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "makeCreditRequest",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "requester",
				"type": "address"
			},
			{
				"internalType": "bool",
				"name": "passed",
				"type": "bool"
			},
			{
				"internalType": "uint256",
				"name": "updatedValue",
				"type": "uint256"
			}
		],
		"name": "postFilterResult",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

def listen_to_events():
    event_filter = w3.eth.filter({
        "address": contract_address,
        "topics": [w3.keccak(text="IncomingRequest(address,uint256)").hex()]
    })

    while True:
        print(str(w3.eth.get_filter_changes(event_filter.filter_id)))
        print("========")
        time.sleep(5) 
        

if __name__ == "__main__":
    print("Listening for PleaseProcessMe events...")
    listen_to_events()



"""
# Read Only Method
def call_contract_method():
    try:
        result = contract.functions.getValue().call()
        print(f"Value Stored in Storage: {result}")
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
"""