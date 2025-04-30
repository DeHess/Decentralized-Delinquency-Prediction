// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "hardhat/console.sol"; 
import "./MockOracle.sol";

contract CreditScorer {
    MockOracle public oracle;
    address private admin;
    mapping(address => bool) public allowedAddresses;

    uint256[] private testData;
    uint64 private oraclePrediction;


    bool public isConsideredOutlier;
    uint256 public ourPrediction;
    uint256 public anomalyScore;

    constructor() {
        admin = msg.sender; 
        oracle = new MockOracle();
        allowedAddresses[admin] = true;
    }

    event AnomalyAudit(address indexed _addr, uint256[] heldData, uint256 prediction);
    event PassOutTree(address indexed _addr, uint256[] heldData);
    event RequestDenied(address indexed _addr, string reason);
    event RequestFail(address indexed _addr, string reason);

    // This Function is called by users
    function makeCreditRequest(uint16 userId) public payable {
        //require(msg.value >= requestPrice, "Insufficient payment to pay for rating service");       
        //(bool success, ) = admin.call{value: msg.value}("");
        //require(success, "Payment transfer to admin failed");
        
        //bool allowed = (block.timestamp >= lastRequestTime[msg.sender] + cooldownTime);
        //if (allowed) {
        //    lastRequestTime[msg.sender] = block.timestamp;
        //    emit AnomalyAudit(msg.sender, value);
        //} else {
        //    emit RequestDenied(msg.sender, "Cooldown period not yet over");
        //}

        testData = oracle.getUserData(userId);
        oraclePrediction = oracle.getUserDelinquencyPrediction(userId);
        emit PassOutTree(msg.sender, testData);
    }      

    //This Function is called by SubTreeContractors dApps
    function writeSubTreeAnswer() public {
        require(allowedAddresses[msg.sender], "This method can only be called by SubTreeContractor");
        ourPrediction = 1;
        emit AnomalyAudit(msg.sender, testData, 1);
    }

    // This Function is called by the Auditor dApp
    function auditResults(address requester, bool isOutlier, uint256 aScore) public {
        require(msg.sender == admin, "Requires admin credentials");
        isConsideredOutlier = isOutlier;
        anomalyScore = aScore;
    }
}