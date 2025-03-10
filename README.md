# nethereum-filter


# First Time setup 
- Nethereum: npm init -y
- Nethereum: npm install --save-dev hardhat
- Nethereum: npm i kill-port -g
- Filterpy: python -m venv venv
- Filterpy: pip install -r requirements.txt


# Run it 
Console 1: Start TestNet
- Nethereum: npx hardhat node

Remix: 
- Connect to Dev Hardhat Provider
- Deploy Contracts
- Copy Address into Program
 
Console 2: Start Python Program
- Filterpy: venv/Scripts/activate
- Filterpy: python SmartContractAccess.py



# Destruct it
Nethereum: kill-port 8545


