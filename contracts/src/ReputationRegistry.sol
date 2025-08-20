// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./interfaces/IReputationRegistry.sol";
import "./interfaces/IIdentityRegistry.sol";

/**
 * @title ReputationRegistry
 * @dev Implementation of the Reputation Registry for ERC-XXXX Trustless Agents v0.3
 * @notice Lightweight entry point for task feedback between agents
 * @author ChaosChain Labs
 */
contract ReputationRegistry is IReputationRegistry {
    // ============ State Variables ============
    
    /// @dev Reference to the IdentityRegistry for agent validation
    IIdentityRegistry public immutable identityRegistry;
    
    /// @dev Mapping from feedback auth ID to whether it exists
    mapping(bytes32 => bool) private _feedbackAuthorizations;
    
    /// @dev Mapping from client-server pair to feedback auth ID
    mapping(uint256 => mapping(uint256 => bytes32)) private _clientServerToAuthId;

    // ============ Constructor ============
    
    /**
     * @dev Constructor sets the identity registry reference
     * @param _identityRegistry Address of the IdentityRegistry contract
     */
    constructor(address _identityRegistry) {
        identityRegistry = IIdentityRegistry(_identityRegistry);
    }

    // ============ Write Functions ============
    
    /**
     * @inheritdoc IReputationRegistry
     */
    function acceptFeedback(uint256 agentClientId, uint256 agentServerId) external {
        // Validate that both agents exist
        if (!identityRegistry.agentExists(agentClientId)) {
            revert AgentNotFound();
        }
        if (!identityRegistry.agentExists(agentServerId)) {
            revert AgentNotFound();
        }
        
        // Get server agent info to check authorization
        IIdentityRegistry.AgentInfo memory serverAgent = identityRegistry.getAgent(agentServerId);
        
        // Only the server agent can authorize feedback
        if (msg.sender != serverAgent.agentAddress) {
            revert UnauthorizedFeedback();
        }
        
        // Check if feedback is already authorized
        bytes32 existingAuthId = _clientServerToAuthId[agentClientId][agentServerId];
        if (existingAuthId != bytes32(0)) {
            revert FeedbackAlreadyAuthorized();
        }
        
        // Generate unique feedback authorization ID
        bytes32 feedbackAuthId = _generateFeedbackAuthId(agentClientId, agentServerId);
        
        // Store the authorization
        _feedbackAuthorizations[feedbackAuthId] = true;
        _clientServerToAuthId[agentClientId][agentServerId] = feedbackAuthId;
        
        emit AuthFeedback(agentClientId, agentServerId, feedbackAuthId);
    }

    // ============ Read Functions ============
    
    /**
     * @inheritdoc IReputationRegistry
     */
    function isFeedbackAuthorized(
        uint256 agentClientId,
        uint256 agentServerId
    ) external view returns (bool isAuthorized, bytes32 feedbackAuthId) {
        feedbackAuthId = _clientServerToAuthId[agentClientId][agentServerId];
        isAuthorized = feedbackAuthId != bytes32(0) && _feedbackAuthorizations[feedbackAuthId];
    }
    
    /**
     * @inheritdoc IReputationRegistry
     */
    function getFeedbackAuthId(
        uint256 agentClientId,
        uint256 agentServerId
    ) external view returns (bytes32 feedbackAuthId) {
        feedbackAuthId = _clientServerToAuthId[agentClientId][agentServerId];
    }

    // ============ Internal Functions ============
    
    /**
     * @dev Generates a unique feedback authorization ID
     * @param agentClientId The client agent ID
     * @param agentServerId The server agent ID
     * @return feedbackAuthId The unique authorization ID
     */
    function _generateFeedbackAuthId(
        uint256 agentClientId,
        uint256 agentServerId
    ) private view returns (bytes32 feedbackAuthId) {
        // Include block timestamp and transaction hash for uniqueness
        feedbackAuthId = keccak256(
            abi.encodePacked(
                agentClientId,
                agentServerId,
                block.timestamp,
                block.difficulty, // Use block.difficulty for additional entropy
                tx.origin
            )
        );
    }
}