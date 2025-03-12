// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CreditScorer {

    
    address private admin;
    uint256 private requestPrice;
    uint256 public cooldownTime = 1 days;
    mapping(address => uint256) public lastRequestTime;


    constructor() {
        admin = msg.sender; 
        requestPrice = 38000000000000;
    }

    // Mock Data
    uint256 private value;

    event IncomingRequest(address indexed _addr, uint256 value);
    event RequestDenied(address indexed _addr, string reason);
    
    event RequestSuccess(address indexed _addr, uint256 value);
    event RequestFail(address indexed _addr);


    function makeCreditRequest() public payable {
        require(msg.value >= requestPrice, "Insufficient payment to pay for rating service");
        // Make sure the Incoming Request is enshrined on the blockchain
        
        (bool success, ) = admin.call{value: msg.value}("");
        require(success, "Payment transfer to admin failed");
        
        bool allowed = (block.timestamp >= lastRequestTime[msg.sender] + cooldownTime);
        if (allowed) {
            lastRequestTime[msg.sender] = block.timestamp;
            emit IncomingRequest(msg.sender, msg.value);
        } else {
            emit RequestDenied(msg.sender, "Cooldown period not yet over");
        }
    }      


    // This method is called by the off-chain Filter Program
    function postFilterResult(address requester, bool passed, uint256 updatedValue) public {
        require(msg.sender == admin, "Requires admin credentials");
        if (passed) {
            value = updatedValue;
            // Make sure the Filter Result is enshrined
            emit RequestSuccess(requester, updatedValue);
        } else { 
            emit RequestFail(requester);
        }
    }

    function getValue() public view returns (uint256) {
        return value;
    }

    function getRequestPrice() public view returns (uint256) {
        return requestPrice;
    }

    function setRequestPrice(uint256 _requestPrice) public {
        require(msg.sender == admin, "Requires admin credentials");
        requestPrice = _requestPrice;
    }
}