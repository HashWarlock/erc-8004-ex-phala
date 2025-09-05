// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./interfaces/IIdentityRegistry.sol";

/**
 * @title IdentityRegistry
 * @dev Implementation of the Identity Registry for ERC-8004 Trustless Agents
 * @notice Central registry for all agent identities with spam protection
 * @author ChaosChain Labs
 */
contract IdentityRegistry is IIdentityRegistry {
    // ============ Constants ============
    
    /// @dev Contract version for tracking implementation changes
    string public constant VERSION = "1.0.0";

    // ============ State Variables ============
    
    /// @dev Counter for agent IDs
    uint256 private _agentIdCounter;
    
    /// @dev Mapping from agent ID to agent info
    mapping(uint256 => AgentInfo) private _agents;
    
    /// @dev Mapping from domain to agent ID
    mapping(string => uint256) private _domainToAgentId;
    
    /// @dev Mapping from address to agent ID
    mapping(address => uint256) private _addressToAgentId;

    // ============ Constructor ============
    
    constructor() {
        // Start agent IDs from 1 (0 is reserved for "not found")
        _agentIdCounter = 1;
    }

    // ============ Write Functions ============
    
    /**
     * @inheritdoc IIdentityRegistry
     */
    function newAgent(
        string calldata agentDomain, 
        address agentAddress
    ) external returns (uint256 agentId) {
        // SECURITY: Only allow registration of own address to prevent impersonation
        if (msg.sender != agentAddress) {
            revert UnauthorizedRegistration();
        }
        
        // Validate inputs
        if (bytes(agentDomain).length == 0) {
            revert InvalidDomain();
        }
        if (agentAddress == address(0)) {
            revert InvalidAddress();
        }
        
        // SECURITY: Normalize domain to lowercase to prevent case-variance bypass
        string memory normalizedDomain = _toLowercase(agentDomain);
        
        // Check for duplicates using normalized domain
        if (_domainToAgentId[normalizedDomain] != 0) {
            revert DomainAlreadyRegistered();
        }
        if (_addressToAgentId[agentAddress] != 0) {
            revert AddressAlreadyRegistered();
        }
        
        // Assign new agent ID
        agentId = _agentIdCounter++;
        
        // Store agent info with original domain (for display) but use normalized for lookups
        _agents[agentId] = AgentInfo({
            agentId: agentId,
            agentDomain: agentDomain, // Store original case for display
            agentAddress: agentAddress
        });
        
        // Create lookup mappings using normalized domain
        _domainToAgentId[normalizedDomain] = agentId;
        _addressToAgentId[agentAddress] = agentId;
        

        
        emit AgentRegistered(agentId, agentDomain, agentAddress);
    }
    
    /**
     * @inheritdoc IIdentityRegistry
     */
    function updateAgent(
        uint256 agentId,
        string calldata newAgentDomain,
        address newAgentAddress
    ) external returns (bool success) {
        // Validate agent exists
        AgentInfo storage agent = _agents[agentId];
        if (agent.agentId == 0) {
            revert AgentNotFound();
        }
        
        // Check authorization
        if (msg.sender != agent.agentAddress) {
            revert UnauthorizedUpdate();
        }
        
        bool domainChanged = bytes(newAgentDomain).length > 0;
        bool addressChanged = newAgentAddress != address(0);
        
        // Validate new values if provided
        if (domainChanged) {
            // SECURITY: Normalize new domain for consistent checking
            string memory normalizedNewDomain = _toLowercase(newAgentDomain);
            if (_domainToAgentId[normalizedNewDomain] != 0) {
                revert DomainAlreadyRegistered();
            }
        }
        
        if (addressChanged) {
            if (_addressToAgentId[newAgentAddress] != 0) {
                revert AddressAlreadyRegistered();
            }
        }
        
        // Update domain if provided
        if (domainChanged) {
            // SECURITY: Remove old domain mapping using normalized version
            string memory oldNormalizedDomain = _toLowercase(agent.agentDomain);
            delete _domainToAgentId[oldNormalizedDomain];
            
            // SECURITY: Add new domain mapping using normalized version
            string memory normalizedNewDomain = _toLowercase(newAgentDomain);
            agent.agentDomain = newAgentDomain; // Store original case for display
            _domainToAgentId[normalizedNewDomain] = agentId;
        }
        
        // Update address if provided
        if (addressChanged) {
            // Remove old address mapping
            delete _addressToAgentId[agent.agentAddress];
            // Set new address
            agent.agentAddress = newAgentAddress;
            _addressToAgentId[newAgentAddress] = agentId;
        }
        
        emit AgentUpdated(agentId, agent.agentDomain, agent.agentAddress);
        return true;
    }

    // ============ Read Functions ============
    
    /**
     * @inheritdoc IIdentityRegistry
     */
    function getAgent(uint256 agentId) external view returns (AgentInfo memory agentInfo) {
        agentInfo = _agents[agentId];
        if (agentInfo.agentId == 0) {
            revert AgentNotFound();
        }
    }
    
    /**
     * @inheritdoc IIdentityRegistry
     */
    function resolveByDomain(string calldata agentDomain) external view returns (AgentInfo memory agentInfo) {
        // SECURITY: Normalize domain for lookup to prevent case-variance bypass
        string memory normalizedDomain = _toLowercase(agentDomain);
        uint256 agentId = _domainToAgentId[normalizedDomain];
        if (agentId == 0) {
            revert AgentNotFound();
        }
        agentInfo = _agents[agentId];
    }
    
    /**
     * @inheritdoc IIdentityRegistry
     */
    function resolveByAddress(address agentAddress) external view returns (AgentInfo memory agentInfo) {
        uint256 agentId = _addressToAgentId[agentAddress];
        if (agentId == 0) {
            revert AgentNotFound();
        }
        agentInfo = _agents[agentId];
    }
    
    /**
     * @inheritdoc IIdentityRegistry
     */
    function getAgentCount() external view returns (uint256 count) {
        return _agentIdCounter - 1; // Subtract 1 because we start from 1
    }
    
    /**
     * @inheritdoc IIdentityRegistry
     */
    function agentExists(uint256 agentId) external view returns (bool exists) {
        return _agents[agentId].agentId != 0;
    }

    // ============ Internal Functions ============
    
    /**
     * @dev Converts a string to lowercase to prevent case-variance bypass attacks
     * @param str The input string to convert
     * @return result The lowercase version of the input string
     */
    function _toLowercase(string memory str) internal pure returns (string memory result) {
        bytes memory strBytes = bytes(str);
        bytes memory resultBytes = new bytes(strBytes.length);
        
        for (uint256 i = 0; i < strBytes.length; i++) {
            // Convert A-Z to a-z
            if (strBytes[i] >= 0x41 && strBytes[i] <= 0x5A) {
                resultBytes[i] = bytes1(uint8(strBytes[i]) + 32);
            } else {
                resultBytes[i] = strBytes[i];
            }
        }
        
        result = string(resultBytes);
    }
}