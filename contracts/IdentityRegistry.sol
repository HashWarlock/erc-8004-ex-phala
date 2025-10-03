// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract IdentityRegistry {
    struct Agent {
        uint256 agentId;
        string agentDomain;
        address agentAddress;
    }

    uint256 public nextAgentId = 1;
    uint256 public constant REGISTRATION_FEE = 0.0001 ether;

    mapping(uint256 => Agent) public agents;
    mapping(string => uint256) public domainToAgentId;
    mapping(address => uint256) public addressToAgentId;

    event AgentRegistered(uint256 indexed agentId, string domain, address agentAddress);

    function newAgent(string calldata domain, address agentAddress) external payable returns (uint256) {
        require(msg.value == REGISTRATION_FEE, "Incorrect fee");
        require(bytes(domain).length > 0, "Empty domain");
        require(agentAddress != address(0), "Zero address");
        require(domainToAgentId[domain] == 0, "Domain registered");
        require(addressToAgentId[agentAddress] == 0, "Address registered");

        uint256 agentId = nextAgentId++;

        agents[agentId] = Agent({
            agentId: agentId,
            agentDomain: domain,
            agentAddress: agentAddress
        });

        domainToAgentId[domain] = agentId;
        addressToAgentId[agentAddress] = agentId;

        emit AgentRegistered(agentId, domain, agentAddress);
        return agentId;
    }

    function resolveByDomain(string calldata domain) external view returns (uint256, string memory, address) {
        uint256 agentId = domainToAgentId[domain];
        require(agentId != 0, "Not found");
        Agent memory agent = agents[agentId];
        return (agent.agentId, agent.agentDomain, agent.agentAddress);
    }

    function resolveByAddress(address agentAddress) external view returns (uint256, string memory, address) {
        uint256 agentId = addressToAgentId[agentAddress];
        require(agentId != 0, "Not found");
        Agent memory agent = agents[agentId];
        return (agent.agentId, agent.agentDomain, agent.agentAddress);
    }

    function getAgent(uint256 agentId) external view returns (uint256, string memory, address) {
        require(agentId > 0 && agentId < nextAgentId, "Invalid ID");
        Agent memory agent = agents[agentId];
        return (agent.agentId, agent.agentDomain, agent.agentAddress);
    }
}
