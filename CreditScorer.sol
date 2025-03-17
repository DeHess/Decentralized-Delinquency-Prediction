// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "hardhat/console.sol"; 

contract CreditScorer {

    address private admin;
    mapping(address => bool) public allowedAddresses;


    constructor() {
        admin = msg.sender; 
        allowedAddresses[admin] = true; //The only allowed subtree contractor is the admin of the smart contract currently
    }

    // Mock Data
    uint256 private value;

    event IncomingRequest(address indexed _addr, uint256 value);
    event PassOutTree(address indexed _addr, uint256 value);
    event RequestDenied(address indexed _addr, string reason);
    event RequestFail(address indexed _addr, string reason);


    function makeCreditRequest() public payable {
        //require(msg.value >= requestPrice, "Insufficient payment to pay for rating service");       
        //(bool success, ) = admin.call{value: msg.value}("");
        //require(success, "Payment transfer to admin failed");
        
        //bool allowed = (block.timestamp >= lastRequestTime[msg.sender] + cooldownTime);
        //if (allowed) {
        //    lastRequestTime[msg.sender] = block.timestamp;
        //    emit IncomingRequest(msg.sender, value);
        //} else {
        //    emit RequestDenied(msg.sender, "Cooldown period not yet over");
        //}

        //Enshrine

        emit IncomingRequest(msg.sender, value);
    }      


    // This method is called by the off-chain Filter dApp
    function postFilterResult(address requester, bool passed, uint256 updatedValue) public {
        require(msg.sender == admin, "Requires admin credentials");
        if (passed) {
            value = updatedValue;
            emit PassOutTree(msg.sender, value);
        } else { 
            emit RequestFail(requester, "Filter said no");
        }
    }

    //This method is called by SubTreeContractors dApps
    function writeSubTreeAnswer() public {
        require(allowedAddresses[msg.sender], "This method can only be called by SubTreeContractor");
        value = value + 1;
        //Write to the result map 
        //If Result Map is complete -> emit ANSWER WE ARE DONE
        //also make sure the result is on the blockchain
    }

    function getValue() public view returns (uint256) {
        return value;
    }
}