import sys
import time
from web3 import Web3
from eth_abi import decode
import pandas as pd
import xgboost as xgb
import json

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

with open('contract_abi.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)


contract = w3.eth.contract(address=contract_address, abi=contract_abi)
model = xgb.Booster()
model.load_model("Model/model.json")

# Smart Contract can't do floats so here we go.
def convert_to_float(val):
    return float(f"0.{int(val):09d}")

def convert_to_int(val):
    return int(round(val * 1_000_000_000))

def post_subtree_results(result):
    transaction = contract.functions.writeSubTreeAnswer(result).build_transaction({
        'chainId': 1337, 
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(account),
    })
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Transaction sent successfully with hash: {txn_hash.hex()}")


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
            data_list[0] = convert_to_float(data[0])
            data_list[3] = convert_to_float(data[3])
            data_list = [data_list]
            columns = ['RevolvingUtilizationOfUnsecuredLines', 'age', 'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio', 'MonthlyIncome','NumberOfOpenCreditLinesAndLoans', 'NumberOfTimes90DaysLate','NumberRealEstateLoansOrLines', 'NumberOfTime60-89DaysPastDueNotWorse','NumberOfDependents']
            df = pd.DataFrame(data_list, columns=columns)
            dmatrix_first = xgb.DMatrix(df)
            tree_pred = model.predict(dmatrix_first, iteration_range=(contractor_id, contractor_id+1))
            print(tree_pred[0])
            post_subtree_results(convert_to_int(tree_pred[0]))
            print("========")

        time.sleep(5)

       
if __name__ == "__main__":
    print(str(g))
    print("Listening for Pass Out Tree Events...")
    listen_for_passout_events()
