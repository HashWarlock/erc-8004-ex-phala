// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./interfaces/IValidationRegistry.sol";
import "./interfaces/IIdentityRegistry.sol";

/**
 * @title ValidationRegistry
 * @dev Implementation of the Validation Registry for ERC-8004 Trustless Agents
 * @notice Provides hooks for requesting and recording independent validation
 * @author ChaosChain Labs
 */
contract ValidationRegistry is IValidationRegistry {
    // ============ Constants ============
    
    /// @dev Contract version for tracking implementation changes
    string public constant VERSION = "1.0.0";
    
    /// @dev Expiration time for validation requests (in seconds)
    uint256 public constant EXPIRATION_TIME = 1000;

    // ============ State Variables ============
    
    /// @dev Reference to the IdentityRegistry for agent validation
    IIdentityRegistry public immutable identityRegistry;
    
    /// @dev Mapping from data hash to validation request
    mapping(bytes32 => IValidationRegistry.Request) private _validationRequests;
    
    /// @dev Mapping from data hash to validation response
    mapping(bytes32 => uint8) private _validationResponses;

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
     * @inheritdoc IValidationRegistry
     */
    function validationRequest(
        uint256 agentValidatorId,
        uint256 agentServerId,
        bytes32 dataHash
    ) external {
        // Validate inputs
        if (dataHash == bytes32(0)) {
            revert InvalidDataHash();
        }
        
        // Validate that both agents exist
        if (!identityRegistry.agentExists(agentValidatorId)) {
            revert AgentNotFound();
        }
        if (!identityRegistry.agentExists(agentServerId)) {
            revert AgentNotFound();
        }
        
        // SECURITY: Prevent self-validation to maintain validation integrity
        if (agentValidatorId == agentServerId) {
            revert SelfValidationNotAllowed();
        }
        
        // Check if request already exists and is still valid
        IValidationRegistry.Request storage existingRequest = _validationRequests[dataHash];
        if (existingRequest.dataHash != bytes32(0)) {
            if (block.timestamp <= existingRequest.timestamp + EXPIRATION_TIME) {
                // SECURITY: Don't emit redundant events to prevent griefing
                // Only allow the original requester to re-emit if needed
                if (existingRequest.agentValidatorId == agentValidatorId && 
                    existingRequest.agentServerId == agentServerId) {
                    // Request already exists - no need to emit event again
                    // This prevents event spam griefing attacks
                }
                return;
            } else {
                // SECURITY: Clear stale response data when request expires
                delete _validationResponses[dataHash];
                // SECURITY: Clear expired request to prevent unbounded growth
                delete _validationRequests[dataHash];
            }
        }
        
        // Create new validation request
        _validationRequests[dataHash] = IValidationRegistry.Request({
            agentValidatorId: agentValidatorId,
            agentServerId: agentServerId,
            dataHash: dataHash,
            timestamp: block.timestamp,
            responded: false
        });
        
        emit ValidationRequestEvent(agentValidatorId, agentServerId, dataHash);
    }
    
    /**
     * @inheritdoc IValidationRegistry
     */
    function validationResponse(bytes32 dataHash, uint8 response) external {
        // Validate response range (0-100)
        if (response > 100) {
            revert InvalidResponse();
        }
        
        // Get the validation request
        IValidationRegistry.Request storage request = _validationRequests[dataHash];
        
        // SECURITY: Use more robust existence check
        if (request.agentValidatorId == 0) {
            revert ValidationRequestNotFound();
        }
        
        // Check if request has expired
        if (block.timestamp > request.timestamp + EXPIRATION_TIME) {
            revert RequestExpired();
        }
        
        // Check if already responded
        if (request.responded) {
            revert ValidationAlreadyResponded();
        }
        
        // Get validator agent info to check authorization
        IIdentityRegistry.AgentInfo memory validatorAgent = identityRegistry.getAgent(request.agentValidatorId);
        
        // Only the designated validator can respond
        if (msg.sender != validatorAgent.agentAddress) {
            revert UnauthorizedValidator();
        }
        
        // Mark as responded and store the response
        request.responded = true;
        _validationResponses[dataHash] = response;
        
        emit ValidationResponseEvent(request.agentValidatorId, request.agentServerId, dataHash, response);
    }

    // ============ Read Functions ============
    
    /**
     * @inheritdoc IValidationRegistry
     */
    function getValidationRequest(bytes32 dataHash) external view returns (IValidationRegistry.Request memory request) {
        request = _validationRequests[dataHash];
        // SECURITY: Use more robust existence check instead of strict equality
        if (request.agentValidatorId == 0) {
            revert ValidationRequestNotFound();
        }
    }
    
    /**
     * @inheritdoc IValidationRegistry
     */
    function isValidationPending(bytes32 dataHash) external view returns (bool exists, bool pending) {
        IValidationRegistry.Request storage request = _validationRequests[dataHash];
        // SECURITY: Use more robust existence check
        exists = request.agentValidatorId != 0;
        
        if (exists) {
            // Check if not expired and not responded
            bool expired = block.timestamp > request.timestamp + EXPIRATION_TIME;
            pending = !expired && !request.responded;
        }
    }
    
    /**
     * @inheritdoc IValidationRegistry
     */
    function getValidationResponse(bytes32 dataHash) external view returns (bool hasResponse, uint8 response) {
        // Check if request exists and has been responded to
        IValidationRegistry.Request storage request = _validationRequests[dataHash];
        hasResponse = request.agentValidatorId != 0 && request.responded;
        if (hasResponse) {
            response = _validationResponses[dataHash];
        }
    }
    
    /**
     * @inheritdoc IValidationRegistry
     */
    function getExpirationSlots() external pure returns (uint256 slots) {
        return EXPIRATION_TIME;
    }
}