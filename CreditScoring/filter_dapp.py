import sys
import time
import numpy as np
from web3 import Web3
from eth_abi import decode
from joblib import load
import pandas as pd
import xgboost as xgb

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

if not w3.is_connected():
    print("Connection failed!")
    exit()

if len(sys.argv) < 3:
    print("Usage: python SmartContractAccess.py <contract_address> <private_key>")
    sys.exit(1)

scaler = model = load("Model/outlier_scaler.pkl")
outlier_detection_model = load("Model/outlier_model.pkl")
account = w3.eth.accounts[0] #TODO this has to be the admin SPECIFICALLY (probably also commandline argument)
private_key = sys.argv[1]
contract_address = sys.argv[2] 
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
			}
		],
		"name": "preFilterResult",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "writeSubTreeAnswer",
		"outputs": [],
		"stateMutability": "view",
		"type": "function"
	}
]

contract = w3.eth.contract(address=contract_address, abi=contract_abi)


def send_pre_filter_results(sender, passed):
    transaction = contract.functions.preFilterResult(sender, passed).build_transaction({
        'chainId': 1337, 
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(account),
    })
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Transaction sent successfully with hash: {txn_hash.hex()}")


def listen_for_incoming_requests():
    incoming_request_filter = w3.eth.filter({
        "address": contract_address,
        "topics": [w3.keccak(text="IncomingRequest(address,uint256[])").hex()]
    })
    
    while True:
        logs = w3.eth.get_filter_changes(incoming_request_filter.filter_id)
        for log in logs:
            sender = "0x" + log["topics"][1].hex()[-40:]
            data_bytes = log["data"]
            data = decode(["uint256[]"], data_bytes)[0]
            data_list = list(data)

            data_list[0] = round(data[0] / 1e9, 7)
            data_list[3] = round(data[3] / 1e9, 7)
            data_list = [data_list]
            print(data_list)
            print(type(data_list))
            columns = ['RevolvingUtilizationOfUnsecuredLines', 'age', 'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio', 'MonthlyIncome','NumberOfOpenCreditLinesAndLoans', 'NumberOfTimes90DaysLate','NumberRealEstateLoansOrLines', 'NumberOfTime60-89DaysPastDueNotWorse','NumberOfDependents']
            df = pd.DataFrame(data_list, columns=columns)
            df = df.to_numpy()
            df = np.nan_to_num(df, nan=0.0)
            entry_scaled = scaler.transform(df)
            is_outlier = outlier_detection_model.predict(entry_scaled)[0]
            if is_outlier == 0:
                send_pre_filter_results(Web3.to_checksum_address(sender), True)
            else:						# TODO Once we are done testing: make this false
                send_pre_filter_results(Web3.to_checksum_address(sender), True) 

            print(f"Sender: {sender}")
            print("Values:", data_list)
            print("Outlier?:", is_outlier)
            print("========")
            
        time.sleep(5)
       
if __name__ == "__main__":
    print("Listening for Requests...")
    listen_for_incoming_requests()







"""
# Read Only Method
def call_contract_method():
    try:
        result = contract.functions.getValue().call()
        print(f"Value Stored in Storage: {result}")
    except Exception as e:
        print(f"Error calling method: {e}")
"""
