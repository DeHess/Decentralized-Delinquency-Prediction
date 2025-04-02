// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "hardhat/console.sol"; 

contract MockOracle {
    mapping(uint16 => uint256[]) private userSecondaryData;
    mapping(uint16 => uint64) private userDelinquencyPrediction;

    constructor() {
        userSecondaryData[1] = [766126609, 45, 2, 802982129, 9120, 13, 0, 6, 0, 2];
        userDelinquencyPrediction[1] = 1;
    }

    function getUserData(uint16 key) public view returns (uint256[] memory) {
        return userSecondaryData[key];
    }
    
    function getUserDelinquencyPrediction(uint16 key) public view returns (uint64) {
        return userDelinquencyPrediction[key];
    }

}