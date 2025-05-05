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
    uint256[] private secondaryData;
    uint64 private oraclePrediction;
    address public currentRequester;
    mapping(address => bool) public hasSubmitted;
    uint256 public submissionCount;
    mapping(address => uint256) public contractorPredictions;

    // === For Dev ===
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

    ContractorSubmission[] public contractorSubmissionsList;
    AuditResult[] public auditReceiptsList;

    // === Events ===
    event AnomalyAudit(address indexed _addr, uint256[] heldData, uint256 prediction);
    event PostAuditResults(address indexed _addr, uint256 prediction, bool outlier, uint256 anomalyScore);
    event PassOutTree(address indexed _addr, uint256[] heldData);

    // === Locking Mechanism ===
    bool public locked; 

    constructor() {
        admin = msg.sender;
        oracle = new MockOracle();
        contractorList.push(admin);
        locked = false; 
    }

    //============ User Function / Entry Point ============  
    function makeCreditRequest(uint16 userId) public payable {
        require(!locked, "A credit scoring request is ongoing and the contract is locked, please try again later.");
        locked = true;
        resetSubmissions();
        currentRequester = msg.sender;
        secondaryData = oracle.getUserData(userId);
        oraclePrediction = oracle.getUserDelinquencyPrediction(userId);
        emit PassOutTree(msg.sender, secondaryData);
    }

    //============ SubTreeContractor dAPPs Function ============  
    function writeSubTreeAnswer(uint256 prediction) public {
        require(isAllowedContractor(msg.sender), "Only contractors can submit");
        require(!hasSubmitted[msg.sender], "Contractor already submitted");

        hasSubmitted[msg.sender] = true;
        submissionCount++;

        contractorSubmissionsList.push(ContractorSubmission({
            requester: currentRequester,
            contractor: msg.sender,
            prediction: prediction,
            timestamp: block.timestamp
        }));

        contractorPredictions[msg.sender] = prediction; 

        if (submissionCount == contractorList.length) {
            uint256 finalisedPrediction = finalizeSubmissions();
            emit AnomalyAudit(msg.sender, secondaryData, finalisedPrediction);
        } 
    }

    //============ Auditor dAPP Function ============  
    function auditResults(address requester, bool isOutlier, uint256 anomalyScore) public {
        require(msg.sender == admin, "Requires admin credentials");

        ourAnomalyScore = anomalyScore;
        ourOutlier = isOutlier;

        auditReceiptsList.push(AuditResult({
            requester: requester,
            prediction: ourPrediction,
            isOutlier: isOutlier,
            anomalyScore: anomalyScore,
            timestamp: block.timestamp
        }));

        emit PostAuditResults(requester, ourPrediction, isOutlier, anomalyScore);

        locked = false;
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
        require(msg.sender == admin, "Only admin can add contractors.");
        require(!isAllowedContractor(addr), "This contractor has already been added.");
        contractorList.push(addr);
    }

    function removeContractor(address addr) public {
        require(msg.sender == admin, "Only admin can remove contractors.");
        require(isAllowedContractor(addr), "This address is not in the list");
        for (uint i = 0; i < contractorList.length; i++) {
            if (contractorList[i] == addr) {
                contractorList[i] = contractorList[contractorList.length - 1];
                contractorList.pop();
                return;
            }
        }
        revert("Contractor address not found.");
    }
}
