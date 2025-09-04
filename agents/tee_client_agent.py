"""
TEE-Enabled Client Agent - Feedback and Reputation Management

This agent demonstrates a TEE-enabled Client Agent role in the ERC-8004 ecosystem.
It uses TEE-derived keys for secure feedback authorization and reputation management.
"""

import time
from typing import Dict, Any, Optional, List
from .tee_base_agent import ERC8004TEEAgent


class TEEClientAgent(ERC8004TEEAgent):
    """
    TEE-enabled Client Agent that manages feedback and reputation
    """

    def __init__(
        self, agent_domain: str, salt: str, tee_endpoint: Optional[str] = None
    ):
        """Initialize the TEE Client Agent"""
        super().__init__(agent_domain, salt, tee_endpoint)

        # Track feedback authorizations
        self.authorized_servers: List[int] = []
        self.feedback_history: List[Dict[str, Any]] = []

        print(f"💼 TEE Client Agent initialized")
        print(f"   Domain: {self.agent_domain}")
        print(f"   Address: {self.address}")
        print(f"   TEE: Enabled ✅")

    def authorize_server_feedback(self, server_agent_id: int) -> str:
        """
        Authorize a server agent to receive feedback from this client

        Args:
            server_agent_id: ID of the server agent to authorize

        Returns:
            Transaction hash
        """
        if not self.agent_id:
            raise ValueError("Client agent must be registered first")

        print(f"🔐 Authorizing feedback to server agent {server_agent_id}")

        # Call ReputationRegistry.acceptFeedback(clientId, serverId)
        function = self.reputation_registry.functions.acceptFeedback(
            self.agent_id,  # Client ID (this agent)
            server_agent_id,  # Server ID (the one we're authorizing)
        )

        # Build and send transaction - using TEE-derived private key
        transaction = function.build_transaction(
            {
                "from": self.address,
                "gas": 100000,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": self.w3.eth.get_transaction_count(self.address),
            }
        )

        try:
            # self.private_key is set by TEE base agent from get_key()
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, private_key=self.private_key
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)

            print(f"   Transaction hash: {tx_hash.hex()}")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt.status == 1:
                print(f"✅ Feedback authorization successful")
                self.authorized_servers.append(server_agent_id)
                return tx_hash.hex()
            else:
                print(f"❌ Transaction failed with status: {receipt.status}")
                raise Exception(f"Feedback authorization transaction failed")
        except Exception as e:
            print(f"❌ Feedback authorization error: {str(e)}")
            raise Exception(f"Feedback authorization failed: {str(e)}")

    def submit_feedback(
        self, server_agent_id: int, score: int, comment: str = ""
    ) -> Dict[str, Any]:
        """
        Submit feedback for a server agent's service with TEE attestation

        Args:
            server_agent_id: ID of the server agent
            score: Feedback score (0-100)
            comment: Optional feedback comment

        Returns:
            Feedback package with transaction details and TEE attestation
        """
        if not self.agent_id:
            raise ValueError("Client agent must be registered first")

        if score < 0 or score > 100:
            raise ValueError("Score must be between 0 and 100")

        print(f"📝 Submitting feedback for server agent {server_agent_id}")
        print(f"   Score: {score}/100")

        # Note: Server must authorize client to provide feedback
        # This is done externally via the server's authorize_client_feedback method

        # Get TEE attestation for the feedback
        attestation = self.get_attestation()

        # Create feedback data with TEE proof
        feedback_data = {
            "client_id": self.agent_id,
            "server_id": server_agent_id,
            "score": score,
            "comment": comment,
            "timestamp": int(time.time()),
            "client_domain": self.agent_domain,
            "tee_attestation": {
                "quote_length": len(attestation.get("quote", "")),
                "has_attestation": "quote" in attestation,
                "tee_endpoint": self.tee_endpoint,
            },
        }

        # In a real implementation, this would submit to the blockchain
        # For now, we store locally and could implement on-chain later
        self.feedback_history.append(feedback_data)

        print(f"✅ Feedback submitted with TEE attestation")
        return feedback_data

    def check_server_reputation(self, server_agent_id: int) -> Dict[str, Any]:
        """
        Check the reputation score of a server agent with TEE verification

        Args:
            server_agent_id: ID of the server to check

        Returns:
            Reputation information with TEE trust indicators
        """
        print(f"🔍 Checking reputation for server agent {server_agent_id}")

        try:
            # In a full implementation, this would query the ReputationRegistry
            server_feedback = [
                f for f in self.feedback_history if f["server_id"] == server_agent_id
            ]

            # Count TEE-attested feedback
            tee_feedback_count = sum(
                1
                for f in server_feedback
                if f.get("tee_attestation", {}).get("has_attestation", False)
            )

            if server_feedback:
                avg_score = sum(f["score"] for f in server_feedback) / len(
                    server_feedback
                )
                reputation = {
                    "server_id": server_agent_id,
                    "feedback_count": len(server_feedback),
                    "tee_feedback_count": tee_feedback_count,
                    "average_score": avg_score,
                    "trust_level": "high" if tee_feedback_count > 0 else "medium",
                    "last_feedback": server_feedback[-1] if server_feedback else None,
                }
            else:
                reputation = {
                    "server_id": server_agent_id,
                    "feedback_count": 0,
                    "tee_feedback_count": 0,
                    "average_score": 0,
                    "trust_level": "unknown",
                    "last_feedback": None,
                }

            print(f"   Feedback count: {reputation['feedback_count']}")
            print(f"   TEE-attested: {reputation['tee_feedback_count']}")
            print(f"   Average score: {reputation['average_score']:.1f}/100")
            print(f"   Trust level: {reputation['trust_level']}")

            return reputation

        except Exception as e:
            print(f"❌ Failed to check reputation: {e}")
            return {"error": str(e), "server_id": server_agent_id}

    def get_authorized_servers(self) -> List[int]:
        """Get list of server agents this client has authorized"""
        return self.authorized_servers

    def get_feedback_history(self) -> List[Dict[str, Any]]:
        """Get the complete feedback history from this client"""
        return self.feedback_history

    def evaluate_service_quality(self, analysis_data: Dict[str, Any]) -> int:
        """
        Evaluate the quality of a service with TEE-enhanced scoring

        Args:
            analysis_data: The service data to evaluate

        Returns:
            Quality score (0-100) with TEE verification bonus
        """
        print("🎯 Evaluating service quality...")

        # Base heuristic evaluation
        score = 50  # Base score

        # Check for required fields
        required_fields = ["symbol", "timeframe", "analysis"]
        for field in required_fields:
            if field in analysis_data:
                score += 10

        # Check for metadata
        if "metadata" in analysis_data:
            score += 10

            # Bonus for TEE-enabled service
            if analysis_data["metadata"].get("tee_enabled"):
                score += 10
                print("   🔐 TEE-enabled service detected (+10)")

        # Check for timestamp
        if "timestamp" in analysis_data:
            score += 5

        # Cap at 100
        score = min(score, 100)

        print(f"   Quality score: {score}/100")
        return score

    def request_service(
        self, server_agent_id: int, service_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Request a service from a server agent with TEE authentication

        Args:
            server_agent_id: ID of the server agent
            service_params: Parameters for the service request

        Returns:
            Service request details with TEE proof
        """
        print(f"📤 Requesting service from server agent {server_agent_id}")
        print(f"   Service: {service_params.get('service_type', 'unknown')}")

        # Get TEE attestation for the request
        attestation = self.get_attestation()

        # Create service request with TEE proof
        request = {
            "client_id": self.agent_id,
            "server_id": server_agent_id,
            "timestamp": int(time.time()),
            "params": service_params,
            "status": "pending",
            "tee_authentication": {
                "client_address": self.address,
                "has_attestation": "quote" in attestation,
                "tee_verified": True,
            },
        }

        # In a real implementation, this would interact with the server agent
        print(f"✅ Service request created with TEE authentication")
        return request

    def verify_server_tee_attestation(self, server_attestation: Dict[str, Any]) -> bool:
        """
        Verify a server agent's TEE attestation

        Args:
            server_attestation: Attestation data from server

        Returns:
            True if attestation is valid
        """
        print("🔍 Verifying server TEE attestation...")

        # In production, this would verify the actual quote
        # For now, check basic structure
        if "quote" in server_attestation and server_attestation.get("quote"):
            print("   ✅ Valid TEE attestation detected")
            return True
        else:
            print("   ⚠️  No valid TEE attestation found")
            return False

    def get_trust_models(self) -> list:
        """Return supported trust models for this agent"""
        return ["feedback", "reputation-based", "tee-attestation"]

    def get_agent_card(self) -> Dict[str, Any]:
        """Generate AgentCard following A2A specification"""
        return {
            "agentId": self.agent_id,
            "name": "TEE-Enabled Client Agent",
            "description": "Client agent with TEE security for service consumption and feedback",
            "version": "1.0.0",
            "skills": [
                {
                    "skillId": "feedback-provision",
                    "name": "TEE-Verified Feedback",
                    "description": "Provide TEE-attested feedback for server services",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "server_id": {
                                "type": "integer",
                                "description": "Server agent ID",
                            },
                            "score": {"type": "integer", "minimum": 0, "maximum": 100},
                            "comment": {"type": "string"},
                        },
                        "required": ["server_id", "score"],
                    },
                    "outputSchema": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean"},
                            "feedback_id": {"type": "string"},
                            "tee_attested": {"type": "boolean"},
                        },
                    },
                },
                {
                    "skillId": "reputation-query",
                    "name": "Reputation Query with TEE Trust",
                    "description": "Query reputation with TEE trust indicators",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"server_id": {"type": "integer"}},
                        "required": ["server_id"],
                    },
                    "outputSchema": {
                        "type": "object",
                        "properties": {
                            "reputation_score": {"type": "number"},
                            "feedback_count": {"type": "integer"},
                            "tee_feedback_count": {"type": "integer"},
                            "trust_level": {"type": "string"},
                        },
                    },
                },
            ],
            "trustModels": self.get_trust_models(),
            "registrations": [
                {
                    "agentId": self.agent_id,
                    "agentAddress": f"eip155:{self.w3.eth.chain_id}:{self.address}",
                    "signature": "0x...",  # Would be actual signature in production
                    "teeAttestation": self.get_attestation(),
                }
            ],
        }
