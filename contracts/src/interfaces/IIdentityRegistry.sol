// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IIdentityRegistry
 * @dev Interface for the Identity Registry as defined in ERC-8004 Trustless Agents
 * @notice This contract serves as the central registry for all agent identities
 */
interface IIdentityRegistry {
    // ============ Events ============
    
    /**
     * @dev Emitted when a new agent is registered
     */
    event AgentRegistered(uint256 indexed agentId, string agentDomain, address agentAddress);
    
    /**
     * @dev Emitted when an agent's information is updated
     */
    event AgentUpdated(uint256 indexed agentId, string agentDomain, address agentAddress);

    // ============ Structs ============
    
    /**
     * @dev Agent information structure
     */
    struct AgentInfo {
        uint256 agentId;
        string agentDomain;
        address agentAddress;
    }

    // ============ Errors ============
    
    error AgentNotFound();
    error UnauthorizedUpdate();
    error UnauthorizedRegistration();
    error InvalidDomain();
    error InvalidAddress();
    error DomainAlreadyRegistered();
    error AddressAlreadyRegistered();

    // ============ Write Functions ============
    
    /**
     * @dev Register a new agent
     * @param agentDomain The domain where the agent's AgentCard is hosted
     * @param agentAddress The EVM address of the agent
     * @return agentId The unique identifier assigned to the agent
     */
    function newAgent(string calldata agentDomain, address agentAddress) external returns (uint256 agentId);
    
    /**
     * @dev Update an existing agent's information
     * @param agentId The agent's unique identifier
     * @param newAgentDomain New domain (empty string to keep current)
     * @param newAgentAddress New address (zero address to keep current)
     * @return success True if update was successful
     * @notice Only callable by the agent's current address or authorized delegate
     */
    function updateAgent(
        uint256 agentId, 
        string calldata newAgentDomain, 
        address newAgentAddress
    ) external returns (bool success);

    // ============ Read Functions ============
    
    /**
     * @dev Get agent information by ID
     * @param agentId The agent's unique identifier
     * @return agentInfo The agent's information
     */
    function getAgent(uint256 agentId) external view returns (AgentInfo memory agentInfo);
    
    /**
     * @dev Resolve agent by domain
     * @param agentDomain The agent's domain
     * @return agentInfo The agent's information
     */
    function resolveByDomain(string calldata agentDomain) external view returns (AgentInfo memory agentInfo);
    
    /**
     * @dev Resolve agent by address
     * @param agentAddress The agent's address
     * @return agentInfo The agent's information
     */
    function resolveByAddress(address agentAddress) external view returns (AgentInfo memory agentInfo);
    
    /**
     * @dev Get the total number of registered agents
     * @return count The total count of registered agents
     */
    function getAgentCount() external view returns (uint256 count);
    
    /**
     * @dev Check if an agent ID exists
     * @param agentId The agent ID to check
     * @return exists True if the agent exists
     */
    function agentExists(uint256 agentId) external view returns (bool exists);


}