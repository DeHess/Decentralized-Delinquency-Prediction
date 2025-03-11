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
- Keep Account Address
- Keep Account Private Key

Remix: 
- Connect to Dev Hardhat Provider
- Ensure you chose the right account with the address you previously copied from the hardhat console
- Deploy Contract
- Keep Contract Address
 
Console 2: Start Python Program
- Filterpy: venv/Scripts/activate
- Filterpy: python SmartContractAccess.py <Contract Address> <Private Key>



# Destruct Network
Nethereum: kill-port 8545


