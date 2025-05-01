// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "hardhat/console.sol"; 
import "./MockOracle.sol";

contract CreditScorer {
    MockOracle public oracle;
    address private admin;
    address[] public contractorList;

    uint256[] private testData;
    uint64 private oraclePrediction;

    // Track contractor submissions
    mapping(address => bool) public hasSubmitted;
    uint256 public submissionCount;

    // Store all contractor predictions
    mapping(address => uint256) public contractorPredictions;

    //Test variables so I dont have to write another dApp
    bool public ourOutlier;
    uint256 public ourPrediction;
    uint256 public ourAnomalyScore;

    //Contractors need to be accountable, save all their predictions 
    struct ContractorSubmission {
        address contractor;
        uint256 prediction;
        uint256 timestamp;
    }
    mapping(address => ContractorSubmission) public contractorSubmissions;

    constructor() {
        admin = msg.sender;
        oracle = new MockOracle();
        contractorList.push(admin);
    }

    event AnomalyAudit(address indexed _addr, uint256[] heldData, uint256 prediction);
    event PostAuditResults(address indexed _addr, uint256 prediction, bool outlier, uint256 anomalyScore);
    event PassOutTree(address indexed _addr, uint256[] heldData);
    event RequestDenied(address indexed _addr, string reason);
    event RequestFail(address indexed _addr, string reason);


    //============ User Function / Entry Point ============
    function makeCreditRequest(uint16 userId) public payable {
        resetSubmissions(); //TODO Re-Entry Attack vector, Solution: lock
        testData = oracle.getUserData(userId);
        oraclePrediction = oracle.getUserDelinquencyPrediction(userId);
        emit PassOutTree(msg.sender, testData);
    }


    //============ SubTreeContractor dAPPs Function ============
    function writeSubTreeAnswer(uint256 prediction) public {
        require(isAllowedContractor(msg.sender), "Only contractors can submit");
        require(!hasSubmitted[msg.sender], "Contractor already submitted");

        hasSubmitted[msg.sender] = true;
        submissionCount++;

        contractorSubmissions[msg.sender] = ContractorSubmission({
            contractor: msg.sender,
            prediction: prediction,
            timestamp: block.timestamp
        });

        //TODO Denial of Service vector, rogue subtree contractor not giving an answer
        if (submissionCount == contractorList.length) {
            uint256 finalisedPrediction = finalizeSubmissions();
            emit AnomalyAudit(msg.sender, testData, finalisedPrediction);
        } 
    }


    //============ Auditor dAPP Function ============
    function auditResults(address requester, bool isOutlier, uint256 anomalyScore) public {
        require(msg.sender == admin, "Requires admin credentials");

        ourAnomalyScore = anomalyScore;
        ourOutlier = isOutlier;
   
        emit PostAuditResults(requester, ourPrediction, isOutlier, anomalyScore);
    }


    //============ Helper Functions ============
    function resetSubmissions() internal {
        for (uint i = 0; i < contractorList.length; i++) {
            hasSubmitted[contractorList[i]] = false;
        }
        submissionCount = 0;
    }

    function finalizeSubmissions() view internal returns (uint256) {
        uint256 sum = 0;
        uint256 count = contractorList.length;
        for (uint i = 0; i < count; i++) {
            sum += contractorPredictions[contractorList[i]];
        }
        require(count > 0, "No contractor submissions"); 
        return sum / count;
    }

    function isAllowedContractor(address addr) internal view returns (bool) {
        for (uint i = 0; i < contractorList.length; i++) {
            if (contractorList[i] == addr) {
                return true;
            }
        }
        return false;
    }

    function addContractor(address addr) public {
        require(msg.sender == admin);
        require(!isAllowedContractor(addr), "This contractor has already added.");
        contractorList.push(addr);
    }
}
