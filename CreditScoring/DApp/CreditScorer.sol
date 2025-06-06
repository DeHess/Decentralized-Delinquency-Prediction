// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "hardhat/console.sol"; 
import "./MockOracle.sol";

contract DelinquencyPredictor {

    // === Infrastructure, Ownership ===
    MockOracle public oracle;
    address private admin;
    address[] public contractorList;
    uint256 public servicePrice;
    uint256 public contractorFee;

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
        uint256 anomalyScore;
        uint256 timestamp;
    }

    ContractorSubmission[] public contractorSubmissionsList;
    AuditResult[] public auditReceiptsList;

    // === Events ===
    event AnomalyAudit(address indexed _addr, uint256[] heldData, uint256 prediction);
    event PostAuditResults(address indexed _addr, uint256 prediction, uint256 anomalyScore);
    event PassOutTree(address indexed _addr, uint256[] heldData);

    // === Locking Mechanism ===
    bool public locked;

    // === Deadline Variables ===
    uint256 public requestStartTime;
    uint256 public submissionDeadline;
    uint256 public constant MAX_WAIT_TIME = 5 minutes;
    bool public finalized;

    constructor() {
        admin = msg.sender;
        oracle = new MockOracle();
        contractorList.push(admin);
        locked = false;
        finalized = false;
        servicePrice = 10 ether;
        contractorFee = 1 ether;
    }

    //============ User Function / Entry Point ============  
    function makeCreditRequest(uint16 userId) public payable {
        require(!locked, "A credit scoring request is ongoing and the contract is locked, please try again later.");
        require(msg.value == servicePrice, "Incorrect payment: check servicePrice attribute.");
        locked = true;
        resetSubmissions();
        finalized = false;
        currentRequester = msg.sender;
        secondaryData = oracle.getUserData(userId);
        oraclePrediction = oracle.getUserDelinquencyPrediction(userId);
        requestStartTime = block.timestamp;
        submissionDeadline = block.timestamp + MAX_WAIT_TIME;
        emit PassOutTree(msg.sender, secondaryData);
    }

    //============ SubTreeContractor dAPPs Function ============  
    function subTreeAnswer(address requester, uint256 prediction) public {
        require(isAllowedContractor(msg.sender), "Only contractors can submit");
        require(!hasSubmitted[msg.sender], "Contractor already submitted");
        require(!finalized, "Submissions are finalized");

        hasSubmitted[msg.sender] = true;
        submissionCount++;

        contractorSubmissionsList.push(ContractorSubmission({
            requester: requester,
            contractor: msg.sender,
            prediction: prediction,
            timestamp: block.timestamp
        }));

        contractorPredictions[msg.sender] = prediction;

        if (submissionCount == contractorList.length) {
            checkDeadlineAndFinalize();
        }
    }

    //============ Deadline Finalization ============  
    function checkDeadlineAndFinalize() public {
        require(!finalized, "Submissions already finalized.");
        require(block.timestamp >= submissionDeadline || submissionCount == contractorList.length, "Deadline not reached and not all contractors have submitted.");

        uint256 minRequired = (contractorList.length * 2) / 3;
        require(submissionCount >= minRequired, "Not enough contractor submissions (2/3 rule).");

        uint256 finalisedPrediction = finalizeSubmissions();
        finalized = true;
        emit AnomalyAudit(msg.sender, secondaryData, finalisedPrediction);

        for (uint i = 0; i < contractorList.length; i++) {
            if (hasSubmitted[contractorList[i]]) {
                address payable contractor = payable(contractorList[i]);
                (bool sent, ) = contractor.call{value: contractorFee}("");
                require(sent, "Failed to send contractor fee");
            }
        }
    }

    //============ Auditor dAPP Function ============  
    function auditResults(address requester, uint256 anomalyScore) public {
        require(msg.sender == admin, "Requires admin credentials");

        ourAnomalyScore = anomalyScore;

        auditReceiptsList.push(AuditResult({
            requester: requester,
            prediction: ourPrediction,
            anomalyScore: anomalyScore,
            timestamp: block.timestamp
        }));

        emit PostAuditResults(requester, ourPrediction, anomalyScore);

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
        uint256 count = 0;
        for (uint i = 0; i < contractorList.length; i++) {
            if (hasSubmitted[contractorList[i]]) {
                sum += contractorPredictions[contractorList[i]];
                count++;
            }
        }
        require(count > 0, "No valid contractor submissions");
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
        require(isAllowedContractor(addr), "This address is not in the contractor list");
        for (uint i = 0; i < contractorList.length; i++) {
            if (contractorList[i] == addr) {
                contractorList[i] = contractorList[contractorList.length - 1];
                contractorList.pop();
                return;
            }
        }
        revert("Contractor address not found.");
    }

    function changeServicePrice(uint256 newPrice) public {
        require(msg.sender == admin, "Only the admin may change the price of the service.");
        require(locked == false, "Cannot change price while contract is locked.");
        servicePrice = newPrice;
    }

    function manualLock() public {
        require(msg.sender == admin, "Only the admin may lock the contract manually.");
        require(locked == false, "The contract is already locked");
        locked = true;
    }

    function manualUnlock() public {
        require(msg.sender == admin, "Only the admin may unlock the contract manually.");
        require(locked == true, "The contract is already unlocked");
        locked = false;
    }
}
