import sys
import time
from web3 import Web3
from eth_abi import decode
import pandas as pd
import xgboost as xgb

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

if not w3.is_connected():
    print("Connection failed!")
    exit()

if len(sys.argv) < 3:
    print("Usage: python SmartContractAccess.py <private_key> <contract_address <contractor_id>")
    sys.exit(1)

account = w3.eth.accounts[0] #TODO this has to be the admin SPECIFICALLY (probably also commandline argument)
private_key = sys.argv[1]
contract_address = sys.argv[2] 
contractor_id = int(sys.argv[3])
contract_abi = [
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
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
				"internalType": "uint256[]",
				"name": "heldData",
				"type": "uint256[]"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "prediction",
				"type": "uint256"
			}
		],
		"name": "AnomalyAudit",
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
				"internalType": "uint256[]",
				"name": "heldData",
				"type": "uint256[]"
			}
		],
		"name": "PassOutTree",
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
				"internalType": "string",
				"name": "reason",
				"type": "string"
			}
		],
		"name": "RequestDenied",
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
				"internalType": "string",
				"name": "reason",
				"type": "string"
			}
		],
		"name": "RequestFail",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "allowedAddresses",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
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
				"name": "isOutlier",
				"type": "bool"
			},
			{
				"internalType": "uint256",
				"name": "anomalyScore",
				"type": "uint256"
			}
		],
		"name": "auditResults",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint16",
				"name": "userId",
				"type": "uint16"
			}
		],
		"name": "makeCreditRequest",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "oracle",
		"outputs": [
			{
				"internalType": "contract MockOracle",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "testValue",
		"outputs": [
			{
				"internalType": "uint16",
				"name": "",
				"type": "uint16"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "writeSubTreeAnswer",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]

contract = w3.eth.contract(address=contract_address, abi=contract_abi)
model = xgb.Booster()
model.load_model("Model/model.json")

def post_subtree_results(result):
    transaction = contract.functions.writeSubTreeAnswer().build_transaction({
        'chainId': 1337, 
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(account),
    })
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Transaction sent successfully with hash: {txn_hash.hex()}")

# We need: Input Array, Id of Subtree


def listen_for_passout_events():
    pass_out_filter = w3.eth.filter({
        "address": contract_address,
        "topics": [w3.keccak(text="PassOutTree(address,uint256[])").hex()]
    })

    while True:
        logs = w3.eth.get_filter_changes(pass_out_filter.filter_id)
        for log in logs:
            sender = "0x" + log["topics"][1].hex()[-40:]
            data_bytes = log["data"]
            data = decode(["uint256[]"], data_bytes)[0]
            data_list = list(data)
            data_list[0] = round(data[0] / 1e9, 7)
            data_list[3] = round(data[3] / 1e9, 7)
            data_list = [data_list]
            columns = ['RevolvingUtilizationOfUnsecuredLines', 'age', 'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio', 'MonthlyIncome','NumberOfOpenCreditLinesAndLoans', 'NumberOfTimes90DaysLate','NumberRealEstateLoansOrLines', 'NumberOfTime60-89DaysPastDueNotWorse','NumberOfDependents']
            df = pd.DataFrame(data_list, columns=columns)
            dmatrix_first = xgb.DMatrix(df)
            tree_pred = model.predict(dmatrix_first, iteration_range=(contractor_id, contractor_id+1))
            print(tree_pred[0])
            post_subtree_results(int(tree_pred[0] * 10**7))
            print("========")

        time.sleep(5)

       
if __name__ == "__main__":
    print("Listening for Pass Out Tree Events...")
    listen_for_passout_events()
