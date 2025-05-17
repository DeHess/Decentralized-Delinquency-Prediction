import sys
import time
import numpy as np
from web3 import Web3
from eth_abi import decode
from joblib import load
import pandas as pd
import xgboost as xgb
from post_processing import postprocess_prediction
from pre_processing import pre_processing
import json



# Load the model
booster = xgb.Booster()
booster.load_model("Model/model.json")

# Smart Contract can't do floats so here we go.
def convert_to_float(val):
    return float(f"0.{int(val):09d}")

def convert_to_int(val):
    return int(round(val * 1_000_000_000_0))

columns = [
    'RevolvingUtilizationOfUnsecuredLines', 'age',
    'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio',
    'MonthlyIncome', 'NumberOfOpenCreditLinesAndLoans',
    'NumberOfTimes90DaysLate', 'NumberRealEstateLoansOrLines',
    'NumberOfTime60-89DaysPastDueNotWorse', 'NumberOfDependents'
]

def get_anomaly_score(data, pred_score):
    prediction = 1 if pred_score > 0.4 else 0
    df_entry = pd.DataFrame([list(data)], columns=columns)
    postproc_results = postprocess_prediction(booster, df_entry, predicted=prediction)
    post_anomaly_score = postproc_results.get("anomaly_score", 0)
    preproc_results = pre_processing(df_entry)
    pre_anomaly_score = preproc_results.get("z_score").values[0]
    return (post_anomaly_score + pre_anomaly_score) / 2

def get_prediction_score(data):
    dmatrix = xgb.DMatrix(pd.DataFrame([data], columns=columns))
    return booster.predict(dmatrix)[0]




w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

if not w3.is_connected():
    print("Connection failed!")
    exit()

if len(sys.argv) < 3:
    print("Usage: python SmartContractAccess.py <contract_address> <private_key>")
    sys.exit(1)

scaler = load("Model/outlier_scaler.pkl")
outlier_detection_model = load("Model/outlier_model.pkl")
model = xgb.XGBClassifier()
model.load_model("Model/model.json")

account = w3.eth.accounts[0] #TODO this has to be the admin SPECIFICALLY (probably also commandline argument)
private_key = sys.argv[1]
contract_address = sys.argv[2] 

with open('contract_abi.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)

contract = w3.eth.contract(address=contract_address, abi=contract_abi)


def send_scores(sender, is_outlier, score):
    transaction = contract.functions.auditResults(sender, is_outlier, score).build_transaction({
        'chainId': 1337, 
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(account),
    })
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Transaction sent successfully with hash: {txn_hash.hex()}")


def listen_for_incoming_audit_requests():
    incoming_request_filter = w3.eth.filter({
        "address": contract_address,
        "topics": [w3.keccak(text="AnomalyAudit(address,uint256[],uint256)").hex()]
    })
    
    while True:
        logs = w3.eth.get_filter_changes(incoming_request_filter.filter_id)
        
        for log in logs:
            sender = "0x" + log["topics"][1].hex()[-40:]
            data_bytes = log["data"]
            data, prediction = decode(["uint256[]", "uint256"], data_bytes)
            data_list = list(data)

            data_list[0] = convert_to_float(data[0])
            data_list[3] = convert_to_float(data[3])
            data_list = [data_list]

            anomaly_score = get_anomaly_score(data, convert_to_float(prediction))
            prediction_score = get_prediction_score(data)

            print(prediction_score)

            """
            columns = ['RevolvingUtilizationOfUnsecuredLines', 'age', 'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio', 'MonthlyIncome','NumberOfOpenCreditLinesAndLoans', 'NumberOfTimes90DaysLate','NumberRealEstateLoansOrLines', 'NumberOfTime60-89DaysPastDueNotWorse','NumberOfDependents']
            df = pd.DataFrame(data_list, columns=columns)
            
            # Preprocessing
            is_outlier = bool(pre_processing(df))

			# Postprocessing
            score, anomaly_score = get_scores(df)
            print(convert_to_float(prediction))
            print("Outlier?: ", is_outlier)
            """
            
            #print(f"Score: ", score)
            #print("Anomaly Score", anomaly_score)						
            send_scores(Web3.to_checksum_address(sender), True, convert_to_int(anomaly_score))


            #print(f"Sender: {sender}")
            #print("Values:", data_list)
            print("========")
            
        time.sleep(5)
       
if __name__ == "__main__":
    print("Listening for Requests...")
    listen_for_incoming_audit_requests()







"""
# Read Only Method
def call_contract_method():
    try:
        result = contract.functions.getValue().call()
        print(f"Value Stored in Storage: {result}")
    except Exception as e:
        print(f"Error calling method: {e}")
"""
