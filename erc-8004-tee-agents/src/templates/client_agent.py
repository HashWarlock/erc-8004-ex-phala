"""
Client Agent Template

Feedback and reputation management agent implementation.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from ..agent.base import BaseAgent, AgentConfig, RegistryAddresses


class ClientAgent(BaseAgent):
    """
    Client agent for feedback and reputation management.

    Handles feedback submission, reputation tracking, and
    service quality assessment in the network.
    """

    def __init__(self, config: AgentConfig, registries: RegistryAddresses):
        """
        Initialize client agent.

        Args:
            config: Agent configuration
            registries: Registry addresses
        """
        super().__init__(config, registries)
        self.feedback_history = []
        self.service_interactions = []
        self.setup_preferences()

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process client request or feedback task.

        Args:
            task_data: Task containing:
                - task_type: 'feedback', 'request', or 'query'
                - target_agent_id: ID of agent to interact with
                - data: Request data or feedback content
                - rating: Optional rating (for feedback)

        Returns:
            Processing result
        """
        print(f"📝 Processing client task: {task_data.get('task_type', 'unknown')}")

        task_type = task_data.get('task_type', 'feedback')
        result = {
            'task_type': task_type,
            'client_id': self.agent_id,
            'timestamp': datetime.utcnow().isoformat()
        }

        try:
            if task_type == 'feedback':
                feedback_result = await self._process_feedback(task_data)
                result.update(feedback_result)
            elif task_type == 'request':
                request_result = await self._process_service_request(task_data)
                result.update(request_result)
            elif task_type == 'query':
                query_result = await self._process_query(task_data)
                result.update(query_result)
            else:
                result['error'] = f"Unknown task type: {task_type}"
                result['status'] = 'error'

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"❌ Error processing client task: {e}")

        return result

    async def _create_agent_card(self) -> Dict[str, Any]:
        """
        Create agent card describing client capabilities.

        Returns:
            Agent card with client capabilities
        """
        return {
            'name': f'client-{self.config.domain}',
            'description': 'TEE-secured client agent for feedback and requests',
            'role': 'client',
            'capabilities': [
                'feedback_submission',
                'reputation_tracking',
                'service_requests',
                'quality_assessment',
                'interaction_history'
            ],
            'trust_models': ['tee_attestation', 'reputation_based'],
            'endpoints': {
                'feedback': f'https://{self.config.domain}/api/feedback',
                'request': f'https://{self.config.domain}/api/request',
                'history': f'https://{self.config.domain}/api/history'
            },
            'preferences': {
                'min_reputation_threshold': 0.7,
                'preferred_validators': [],
                'max_response_time': '5s'
            },
            'version': '1.0.0'
        }

    def setup_preferences(self):
        """Setup client preferences and thresholds."""
        self.preferences = {
            'min_reputation': 0.7,
            'max_fee': 0.01,  # ETH
            'preferred_response_time': 3.0,  # seconds
            'require_tee_attestation': True
        }
        print("🎯 Client preferences configured")

    # Client-specific Methods
    async def _process_feedback(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process feedback submission.

        Args:
            task_data: Feedback data

        Returns:
            Feedback submission result
        """
        target_agent_id = task_data.get('target_agent_id')
        rating = task_data.get('rating', 3)
        comment = task_data.get('comment', '')
        service_data = task_data.get('data', {})

        # Validate rating
        rating = max(1, min(5, int(rating)))

        # Prepare feedback data
        feedback_data = {
            'service_type': service_data.get('service_type', 'general'),
            'quality_score': rating,
            'comment': comment,
            'interaction_id': service_data.get('interaction_id'),
            'timestamp': datetime.utcnow().isoformat()
        }

        # Submit to reputation registry
        tx_hash = None
        if self.is_registered and target_agent_id:
            tx_hash = await self.submit_reputation_feedback(
                target_agent_id,
                rating,
                feedback_data
            )

        # Store in history
        self.feedback_history.append({
            'target_agent_id': target_agent_id,
            'rating': rating,
            'timestamp': feedback_data['timestamp'],
            'tx_hash': tx_hash
        })

        return {
            'status': 'submitted',
            'target_agent_id': target_agent_id,
            'rating': rating,
            'tx_hash': tx_hash,
            'feedback_data': feedback_data
        }

    async def _process_service_request(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process service request.

        Args:
            task_data: Service request data

        Returns:
            Service request result
        """
        target_agent_id = task_data.get('target_agent_id')
        service_type = task_data.get('service_type', 'analysis')
        request_data = task_data.get('data', {})

        # Create service request
        request = {
            'requester_id': self.agent_id,
            'service_type': service_type,
            'parameters': request_data,
            'max_fee': self.preferences['max_fee'],
            'timeout': self.preferences['preferred_response_time']
        }

        # Store interaction
        interaction_id = f"req_{datetime.utcnow().timestamp()}"
        self.service_interactions.append({
            'interaction_id': interaction_id,
            'target_agent_id': target_agent_id,
            'service_type': service_type,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'pending'
        })

        return {
            'status': 'requested',
            'interaction_id': interaction_id,
            'target_agent_id': target_agent_id,
            'request': request
        }

    async def _process_query(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process information query.

        Args:
            task_data: Query data

        Returns:
            Query result
        """
        query_type = task_data.get('query_type', 'status')

        if query_type == 'reputation':
            return await self._query_reputation(task_data)
        elif query_type == 'history':
            return await self._query_history(task_data)
        elif query_type == 'recommendations':
            return await self._get_recommendations(task_data)
        else:
            return {
                'status': 'unknown_query',
                'query_type': query_type
            }

    async def _query_reputation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query agent reputation.

        Args:
            task_data: Query parameters

        Returns:
            Reputation information
        """
        target_agent_id = task_data.get('target_agent_id')

        if target_agent_id and self.is_registered:
            # Query from registry
            reputation = await self._registry_client.get_reputation(target_agent_id)
            return {
                'status': 'success',
                'agent_id': target_agent_id,
                'reputation': reputation
            }

        return {
            'status': 'error',
            'error': 'Invalid agent ID or not registered'
        }

    async def _query_history(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query interaction history.

        Args:
            task_data: Query parameters

        Returns:
            Interaction history
        """
        limit = task_data.get('limit', 10)
        filter_type = task_data.get('filter', 'all')

        history = []
        if filter_type in ['all', 'feedback']:
            history.extend([
                {'type': 'feedback', **f}
                for f in self.feedback_history[-limit:]
            ])

        if filter_type in ['all', 'service']:
            history.extend([
                {'type': 'service', **s}
                for s in self.service_interactions[-limit:]
            ])

        # Sort by timestamp
        history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return {
            'status': 'success',
            'history': history[:limit],
            'total_feedback': len(self.feedback_history),
            'total_interactions': len(self.service_interactions)
        }

    async def _get_recommendations(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get service provider recommendations.

        Args:
            task_data: Recommendation criteria

        Returns:
            Recommended agents
        """
        service_type = task_data.get('service_type', 'general')

        # Placeholder for recommendation logic
        # In production, query registry and filter by reputation
        recommendations = [
            {
                'agent_id': 1,
                'reputation_score': 0.95,
                'service_type': service_type,
                'estimated_fee': 0.001
            },
            {
                'agent_id': 2,
                'reputation_score': 0.88,
                'service_type': service_type,
                'estimated_fee': 0.0008
            }
        ]

        return {
            'status': 'success',
            'service_type': service_type,
            'recommendations': recommendations
        }

    # Utility Methods
    async def submit_feedback(
        self,
        target_agent_id: int,
        rating: int,
        comment: str = ''
    ) -> str:
        """
        Submit feedback for an agent.

        Args:
            target_agent_id: ID of agent to rate
            rating: Rating (1-5)
            comment: Optional comment

        Returns:
            Transaction hash
        """
        task_data = {
            'task_type': 'feedback',
            'target_agent_id': target_agent_id,
            'rating': rating,
            'comment': comment
        }

        result = await self.process_task(task_data)
        return result.get('tx_hash', '')

    async def request_service(
        self,
        target_agent_id: int,
        service_type: str,
        parameters: Dict[str, Any]
    ) -> str:
        """
        Request service from an agent.

        Args:
            target_agent_id: ID of service provider
            service_type: Type of service requested
            parameters: Service parameters

        Returns:
            Interaction ID
        """
        task_data = {
            'task_type': 'request',
            'target_agent_id': target_agent_id,
            'service_type': service_type,
            'data': parameters
        }

        result = await self.process_task(task_data)
        return result.get('interaction_id', '')

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get client statistics.

        Returns:
            Client activity statistics
        """
        return {
            'total_feedback_submitted': len(self.feedback_history),
            'total_service_requests': len(self.service_interactions),
            'average_rating_given': sum(f['rating'] for f in self.feedback_history) / len(self.feedback_history) if self.feedback_history else 0,
            'active_since': self.feedback_history[0]['timestamp'] if self.feedback_history else None
        }