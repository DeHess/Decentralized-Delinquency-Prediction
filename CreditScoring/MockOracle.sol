// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "hardhat/console.sol"; 

contract MockOracle {
    mapping(uint16 => uint256[]) private userSecondaryData;
    mapping(uint16 => uint64) private userDelinquencyPrediction;

    constructor() {
        userSecondaryData[1] = [766126609, 45, 2, 802982129, 9120, 13, 0, 6, 0, 2];
        userDelinquencyPrediction[1] = 1;

        // Column Discrepancy: unreasonable Age
        userSecondaryData[2] = [766126609, 301, 2, 802982129, 9120, 13, 0, 6, 0, 2];
        userDelinquencyPrediction[2] = 1;
        
        // Entirety Discrepancy: Delinquency Transitivity
        // If a borrower was delinquent 60-89 Days Past Due exactly once, 
        // they must have been 30-59 Days Past Due at least once
        userSecondaryData[3] = [88,0,0,64,0,0,3200,0,0,0,1,0];
        userDelinquencyPrediction[3] = 1;

        

    }

    function getUserData(uint16 key) public view returns (uint256[] memory) {
        return userSecondaryData[key];
    }
    
    function getUserDelinquencyPrediction(uint16 key) public view returns (uint64) {
        return userDelinquencyPrediction[key];
    }

}