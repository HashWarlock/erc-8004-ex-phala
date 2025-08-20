// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IReputationRegistry
 * @dev Interface for the Reputation Registry as defined in ERC-XXXX Trustless Agents v0.3
 * @notice This contract provides a lightweight entry point for task feedback between agents
 */
interface IReputationRegistry {
    // ============ Events ============
    
    /**
     * @dev Emitted when feedback is authorized for a client-server pair
     */
    event AuthFeedback(
        uint256 indexed agentClientId,
        uint256 indexed agentServerId,
        bytes32 indexed feedbackAuthId
    );

    // ============ Errors ============
    
    error AgentNotFound();
    error UnauthorizedFeedback();
    error FeedbackAlreadyAuthorized();
    error InvalidAgentId();

    // ============ Write Functions ============
    
    /**
     * @dev Accept feedback authorization from a client agent
     * @param agentClientId The ID of the client agent who will provide feedback
     * @param agentServerId The ID of the server agent who will receive feedback
     * @notice This creates a unique authorization for the client to provide feedback
     * @notice Only callable by the server agent's registered address
     */
    function acceptFeedback(uint256 agentClientId, uint256 agentServerId) external;

    // ============ Read Functions ============
    
    /**
     * @dev Check if feedback is authorized for a client-server pair
     * @param agentClientId The client agent ID
     * @param agentServerId The server agent ID
     * @return isAuthorized True if feedback is authorized
     * @return feedbackAuthId The unique authorization ID if authorized
     */
    function isFeedbackAuthorized(
        uint256 agentClientId, 
        uint256 agentServerId
    ) external view returns (bool isAuthorized, bytes32 feedbackAuthId);
    
    /**
     * @dev Get the feedback authorization ID for a client-server pair
     * @param agentClientId The client agent ID
     * @param agentServerId The server agent ID
     * @return feedbackAuthId The unique authorization ID
     */
    function getFeedbackAuthId(
        uint256 agentClientId, 
        uint256 agentServerId
    ) external view returns (bytes32 feedbackAuthId);
}