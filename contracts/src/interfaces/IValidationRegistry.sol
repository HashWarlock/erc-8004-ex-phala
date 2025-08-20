// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IValidationRegistry
 * @dev Interface for the Validation Registry as defined in ERC-XXXX Trustless Agents v0.3
 * @notice This contract provides hooks for requesting and recording independent validation
 */
interface IValidationRegistry {
    // ============ Events ============
    
    /**
     * @dev Emitted when a validation request is made
     */
    event ValidationRequestEvent(
        uint256 indexed agentValidatorId,
        uint256 indexed agentServerId,
        bytes32 indexed dataHash
    );
    
    /**
     * @dev Emitted when a validation response is submitted
     */
    event ValidationResponseEvent(
        uint256 indexed agentValidatorId,
        uint256 indexed agentServerId,
        bytes32 indexed dataHash,
        uint8 response
    );

    // ============ Structs ============
    
    /**
     * @dev Validation request structure
     */
    struct Request {
        uint256 agentValidatorId;
        uint256 agentServerId;
        bytes32 dataHash;
        uint256 timestamp;
        bool responded;
    }

    // ============ Errors ============
    
    error AgentNotFound();
    error ValidationRequestNotFound();
    error ValidationAlreadyResponded();
    error UnauthorizedValidator();
    error RequestExpired();
    error InvalidResponse();
    error InvalidDataHash();

    // ============ Write Functions ============
    
    /**
     * @dev Submit a validation request
     * @param agentValidatorId The ID of the validator agent
     * @param agentServerId The ID of the server agent whose work needs validation
     * @param dataHash Hash of the data to be validated
     * @notice Creates a validation request that can be responded to by the validator
     */
    function validationRequest(
        uint256 agentValidatorId,
        uint256 agentServerId,
        bytes32 dataHash
    ) external;
    
    /**
     * @dev Submit a validation response
     * @param dataHash Hash of the data that was validated
     * @param response Validation score (0-100)
     * @notice Only callable by the designated validator agent's address
     */
    function validationResponse(bytes32 dataHash, uint8 response) external;

    // ============ Read Functions ============
    
    /**
     * @dev Get validation request details
     * @param dataHash The hash of the data being validated
     * @return request The validation request details
     */
    function getValidationRequest(bytes32 dataHash) external view returns (Request memory request);
    
    /**
     * @dev Check if a validation request exists and is pending
     * @param dataHash The hash of the data being validated
     * @return exists True if the request exists
     * @return pending True if the request is still pending response
     */
    function isValidationPending(bytes32 dataHash) external view returns (bool exists, bool pending);
    
    /**
     * @dev Get the validation response for a data hash
     * @param dataHash The hash of the validated data
     * @return hasResponse True if a response exists
     * @return response The validation score (0-100)
     */
    function getValidationResponse(bytes32 dataHash) external view returns (bool hasResponse, uint8 response);
    
    /**
     * @dev Get the expiration time for validation requests
     * @return slots Number of storage slots a request remains valid
     */
    function getExpirationSlots() external view returns (uint256 slots);
}