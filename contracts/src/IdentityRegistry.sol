// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./interfaces/IIdentityRegistry.sol";

/**
 * @title IdentityRegistry
 * @dev Implementation of the Identity Registry for ERC-XXXX Trustless Agents v0.3
 * @notice Central registry for all agent identities with spam protection
 * @author ChaosChain Labs
 */
contract IdentityRegistry is IIdentityRegistry {
    // ============ Constants ============
    
    /// @dev Registration fee of 0.005 ETH that gets burned
    uint256 public constant REGISTRATION_FEE = 0.005 ether;

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
    ) external payable returns (uint256 agentId) {
        // Validate fee
        if (msg.value != REGISTRATION_FEE) {
            revert InsufficientFee();
        }
        
        // Validate inputs
        if (bytes(agentDomain).length == 0) {
            revert InvalidDomain();
        }
        if (agentAddress == address(0)) {
            revert InvalidAddress();
        }
        
        // Check for duplicates
        if (_domainToAgentId[agentDomain] != 0) {
            revert DomainAlreadyRegistered();
        }
        if (_addressToAgentId[agentAddress] != 0) {
            revert AddressAlreadyRegistered();
        }
        
        // Assign new agent ID
        agentId = _agentIdCounter++;
        
        // Store agent info
        _agents[agentId] = AgentInfo({
            agentId: agentId,
            agentDomain: agentDomain,
            agentAddress: agentAddress
        });
        
        // Create lookup mappings
        _domainToAgentId[agentDomain] = agentId;
        _addressToAgentId[agentAddress] = agentId;
        
        // Burn the registration fee by not forwarding it anywhere
        // The ETH stays locked in this contract forever
        
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
            if (_domainToAgentId[newAgentDomain] != 0) {
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
            // Remove old domain mapping
            delete _domainToAgentId[agent.agentDomain];
            // Set new domain
            agent.agentDomain = newAgentDomain;
            _domainToAgentId[newAgentDomain] = agentId;
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
        uint256 agentId = _domainToAgentId[agentDomain];
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
    
    // Note: Registration fee is burned by keeping it locked in this contract
    // This is more gas-efficient than transferring to address(0)
}