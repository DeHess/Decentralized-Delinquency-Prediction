// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "hardhat/console.sol"; 
import "./MockOracle.sol";

contract CreditScorer {
    
    
    // === Infrastructure, Ownership ===
    MockOracle public oracle;
    address private admin;
    address[] public contractorList;

    // === Volatile Variables
    uint256[] private testData;
    uint64 private oraclePrediction;
    address public currentRequester;
    mapping(address => bool) public hasSubmitted;
    uint256 public submissionCount;
    mapping(address => uint256) public contractorPredictions;

    // == For Dev ===
    bool public ourOutlier;
    uint256 public ourPrediction;
    uint256 public ourAnomalyScore;

    // === Accountability, "Receipts" ===
    struct ContractorSubmission {
        address contractor;
        address requester;
        uint256 prediction;
        uint256 timestamp;
    }
    struct AuditResult {
        address requester;
        uint256 prediction;
        bool isOutlier;
        uint256 anomalyScore;
        uint256 timestamp;
    }
    mapping(address => ContractorSubmission) public contractorSubmissions;
    mapping(address => AuditResult[]) public auditReceipts;


    // === Events ===
    event AnomalyAudit(address indexed _addr, uint256[] heldData, uint256 prediction);
    event PostAuditResults(address indexed _addr, uint256 prediction, bool outlier, uint256 anomalyScore);
    event PassOutTree(address indexed _addr, uint256[] heldData);

    constructor() {
        admin = msg.sender;
        oracle = new MockOracle();
        contractorList.push(admin);
    }


    //============ User Function / Entry Point ============
    function makeCreditRequest(uint16 userId) public payable {
        resetSubmissions(); //TODO Re-Entry Attack vector, Solution: lock
        currentRequester = msg.sender;
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
            requester: currentRequester,
            contractor: msg.sender,
            prediction: prediction,
            timestamp: block.timestamp
        });

        contractorPredictions[msg.sender] = prediction; 

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

        auditReceipts[requester].push(AuditResult({
            requester: requester,
            prediction: ourPrediction,
            isOutlier: isOutlier,
            anomalyScore: anomalyScore,
            timestamp: block.timestamp
        }));

        emit PostAuditResults(requester, ourPrediction, isOutlier, anomalyScore);
    }


    //============ Helper Functions ============
    function resetSubmissions() internal {
        for (uint i = 0; i < contractorList.length; i++) {
            hasSubmitted[contractorList[i]] = false;
        }
        submissionCount = 0;
    }

    function finalizeSubmissions() internal returns (uint256) {
        uint256 sum = 0;
        uint256 count = contractorList.length;
        for (uint i = 0; i < count; i++) {
            sum += contractorPredictions[contractorList[i]];
        }
        require(count > 0, "No contractor submissions"); 
        uint256 pred = sum / count;
        ourPrediction = pred;
        return pred;
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
