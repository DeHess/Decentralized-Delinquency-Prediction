// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "hardhat/console.sol"; 
import "./MockOracle.sol";

contract CreditScorer {
    MockOracle public oracle;
    uint256[] private testData;
    uint64 private oracleResult;
    address private admin;
    mapping(address => bool) public allowedAddresses;


    constructor() {
        admin = msg.sender; 
        oracle = new MockOracle();
        allowedAddresses[admin] = true;
    }

    event IncomingRequest(address indexed _addr, uint256[] heldData, uint256 prediction);
    event PassOutTree(address indexed _addr, uint256[] heldData);
    event RequestDenied(address indexed _addr, string reason);
    event RequestFail(address indexed _addr, string reason);


    function makeCreditRequest(uint16 userId) public payable {
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

        testData = oracle.getUserData(userId);
        oracleResult = oracle.getUserDelinquencyPrediction(userId);
        emit IncomingRequest(msg.sender, testData, 1);
    }      


    // This method is called by the off-chain Filter-dApp
    function preFilterResult(address requester, bool passed) public {
        require(msg.sender == admin, "Requires admin credentials");
        if (passed) {
            emit PassOutTree(msg.sender, testData);
        } else { 
            emit RequestFail(requester, "Filter said no");
        }
    }

    //This method is called by SubTreeContractors dApps
    function writeSubTreeAnswer() public view {
        require(allowedAddresses[msg.sender], "This method can only be called by SubTreeContractor");

        //Write to the result map 
        //If Result Map is complete -> emit ANSWER WE ARE DONE
        //also make sure the result is on the blockchain
    }
}