"""
Custom Agent Template

Minimal template for custom agent implementations.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from ..agent.base import BaseAgent, AgentConfig, RegistryAddresses


class CustomAgent(BaseAgent):
    """
    Custom agent template for specialized implementations.

    This is a minimal template that developers can extend
    with their own custom logic and capabilities.
    """

    def __init__(self, config: AgentConfig, registries: RegistryAddresses):
        """
        Initialize custom agent.

        Args:
            config: Agent configuration
            registries: Registry addresses
        """
        super().__init__(config, registries)

        # Add your custom initialization here
        self.custom_data = {}
        self.initialize_custom_features()

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming task with custom logic.

        Override this method to implement your custom task processing.

        Args:
            task_data: Task data to process

        Returns:
            Processing result
        """
        print(f"🔧 Processing custom task: {task_data.get('task_id', 'unknown')}")

        # Extract task information
        task_id = task_data.get('task_id', 'unknown')
        task_type = task_data.get('task_type', 'custom')
        data = task_data.get('data', {})

        # Build result structure
        result = {
            'task_id': task_id,
            'agent_id': self.agent_id,
            'task_type': task_type,
            'status': 'processing',
            'timestamp': datetime.utcnow().isoformat()
        }

        try:
            # ========================================
            # ADD YOUR CUSTOM PROCESSING LOGIC HERE
            # ========================================

            # Example: Simple echo service
            if task_type == 'echo':
                result['echo'] = data
                result['status'] = 'completed'

            # Example: Custom computation
            elif task_type == 'compute':
                computation_result = await self.perform_custom_computation(data)
                result['computation'] = computation_result
                result['status'] = 'completed'

            # Example: Data transformation
            elif task_type == 'transform':
                transformed = await self.transform_data(data)
                result['transformed_data'] = transformed
                result['status'] = 'completed'

            else:
                # Default custom processing
                processed = await self.custom_process(data)
                result['processed'] = processed
                result['status'] = 'completed'

            # ========================================
            # END CUSTOM LOGIC
            # ========================================

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"❌ Error in custom processing: {e}")

        return result

    async def _create_agent_card(self) -> Dict[str, Any]:
        """
        Create agent card describing custom capabilities.

        Customize this method to describe your agent's specific capabilities.

        Returns:
            Agent card with custom capabilities
        """
        return {
            'name': f'custom-{self.config.domain}',
            'description': 'Custom TEE-secured agent implementation',
            'role': 'custom',
            'capabilities': [
                # Add your custom capabilities here
                'custom_processing',
                'data_transformation',
                'specialized_computation'
            ],
            'trust_models': ['tee_attestation'],
            'endpoints': {
                'process': f'https://{self.config.domain}/api/process',
                'status': f'https://{self.config.domain}/api/status',
                # Add your custom endpoints here
            },
            'custom_features': {
                # Add descriptions of your custom features
                'feature_1': 'Description of feature 1',
                'feature_2': 'Description of feature 2'
            },
            'version': '1.0.0'
        }

    # ============================================
    # CUSTOM METHODS - Implement your logic here
    # ============================================

    def initialize_custom_features(self):
        """
        Initialize custom features and configurations.

        Override this method to set up your custom agent features.
        """
        # Example initialization
        self.custom_config = {
            'feature_enabled': True,
            'processing_mode': 'advanced',
            'cache_size': 100
        }

        print("🎨 Custom agent features initialized")

    async def perform_custom_computation(self, data: Dict[str, Any]) -> Any:
        """
        Perform custom computation.

        Args:
            data: Input data for computation

        Returns:
            Computation result
        """
        # Implement your custom computation logic here

        # Example: Simple aggregation
        if isinstance(data, dict) and 'values' in data:
            values = data['values']
            return {
                'sum': sum(values),
                'average': sum(values) / len(values) if values else 0,
                'count': len(values)
            }

        return {'result': 'computed'}

    async def transform_data(self, data: Any) -> Any:
        """
        Transform data according to custom rules.

        Args:
            data: Data to transform

        Returns:
            Transformed data
        """
        # Implement your data transformation logic here

        # Example: Convert to uppercase if string
        if isinstance(data, str):
            return data.upper()
        elif isinstance(data, dict):
            return {k: v.upper() if isinstance(v, str) else v
                   for k, v in data.items()}

        return data

    async def custom_process(self, data: Any) -> Any:
        """
        Default custom processing method.

        Args:
            data: Data to process

        Returns:
            Processed data
        """
        # Implement your default processing logic here

        return {
            'processed': True,
            'data_type': type(data).__name__,
            'timestamp': datetime.utcnow().isoformat(),
            'custom_field': 'Add your custom processing result here'
        }

    # ============================================
    # PLUGIN EXAMPLES
    # ============================================

    def add_custom_plugin(self, plugin_name: str, plugin_config: Dict[str, Any]):
        """
        Add a custom plugin to extend functionality.

        Args:
            plugin_name: Name of the plugin
            plugin_config: Plugin configuration
        """
        # Example of adding a custom plugin
        class CustomPlugin:
            def __init__(self, config):
                self.config = config

            async def execute(self, data):
                # Plugin logic here
                return f"Plugin {plugin_name} processed: {data}"

        plugin = CustomPlugin(plugin_config)
        self.add_plugin(plugin_name, plugin)

    # ============================================
    # UTILITY METHODS
    # ============================================

    def get_custom_metrics(self) -> Dict[str, Any]:
        """
        Get custom agent metrics.

        Returns:
            Custom metrics dictionary
        """
        return {
            'custom_tasks_processed': len(self.custom_data),
            'active_features': list(self.custom_config.keys()),
            'plugins_loaded': self.list_plugins(),
            'status': 'operational'
        }

    async def handle_special_request(
        self,
        request_type: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """
        Handle special custom requests.

        Args:
            request_type: Type of special request
            parameters: Request parameters

        Returns:
            Request result
        """
        # Add your special request handling here

        if request_type == 'custom_query':
            return {'query_result': 'Your custom query result'}
        elif request_type == 'custom_action':
            return {'action_result': 'Your custom action result'}

        return {'error': f'Unknown request type: {request_type}'}