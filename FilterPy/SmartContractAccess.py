from web3 import Web3

# Connect to your local Hardhat testnet
# Replace with your actual Hardhat RPC URL (usually it's something like `http://127.0.0.1:8545` or similar)
infura_url = 'http://127.0.0.1:8545'
w3 = Web3(Web3.HTTPProvider(infura_url))

# Check if we're connected
if not w3.is_connected():
    print("Connection failed!")
    exit()


# The address of the deployed smart contract
contract_address = '0x5FbDB2315678afecb367f032d93F642f64180aa3'  # Replace with your contract address

# ABI (Application Binary Interface) of your contract. You can get this from your contract's compilation artifacts.
# Replace this with the ABI of the contract you're working with.
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

# Initialize the contract object
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Example: Assuming the contract has a method `getValue()`
def call_contract_method():
    # Call a method of the smart contract (read-only)
    try:
        result = contract.functions.getValue().call()
        print(f"Result from contract method: {result}")
    except Exception as e:
        print(f"Error calling method: {e}")

# Example: Sending a transaction (for methods that alter the blockchain state)
def send_transaction():
    # Replace with the account details you want to use to send a transaction
    account = w3.eth.accounts[0]  # You can replace this with the private key of the account

    # To interact with a method that requires gas (such as state-changing methods)
    transaction = contract.functions.setValue(42).buildTransaction({
        'chainId': 1337,  # Hardhat default network ID (replace with your network's ID if different)
        'gas': 2000000,  # Adjust gas limit if necessary
        'gasPrice': w3.toWei('20', 'gwei'),
        'nonce': w3.eth.getTransactionCount(account),
    })

    # Sign the transaction (replace with your private key)
    private_key = '0xYourPrivateKeyHere'  # Never hardcode private keys in real applications
    signed_txn = w3.eth.account.signTransaction(transaction, private_key)

    # Send the transaction
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f"Transaction sent with hash: {txn_hash.hex()}")

# Choose the method to call
call_contract_method()  # Call the read-only method
# send_transaction()  # Uncomment this to send a transaction that modifies the blockchain state
