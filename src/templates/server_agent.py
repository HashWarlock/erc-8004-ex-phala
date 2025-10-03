"""Server Agent - AIO Sandbox Integration"""

import os
import httpx
from datetime import datetime
from typing import Dict, Any
from ..agent.base import BaseAgent, AgentConfig, RegistryAddresses


class ServerAgent(BaseAgent):
    """Server agent with AIO Sandbox integration."""

    def __init__(self, config: AgentConfig, registries: RegistryAddresses, sandbox_url: str = None):
        super().__init__(config, registries)
        self.sandbox_url = sandbox_url or os.getenv("SANDBOX_URL", "http://localhost:8080")
        print(f"📦 Sandbox: {self.sandbox_url}")

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task via AIO Sandbox."""
        data = task_data.get('data', {})
        task_type = data.get('type', 'shell')

        if task_type == 'shell':
            return await self._execute_shell(data.get('command', 'echo "No command"'))
        elif task_type == 'file_read':
            return await self._read_file(data.get('path'))
        elif task_type == 'file_write':
            return await self._write_file(data.get('path'), data.get('content'))
        else:
            return {"error": "Unknown task type", "type": task_type}

    async def _execute_shell(self, command: str) -> Dict[str, Any]:
        """Execute shell command via sandbox."""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.sandbox_url}/v1/shell/exec",
                    json={"command": command},
                    timeout=30.0
                )
                return resp.json()
            except Exception as e:
                return {"error": str(e)}

    async def _read_file(self, path: str) -> Dict[str, Any]:
        """Read file via sandbox."""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.sandbox_url}/v1/file/read",
                    json={"file": path},
                    timeout=10.0
                )
                return resp.json()
            except Exception as e:
                return {"error": str(e)}

    async def _write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write file via sandbox."""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.sandbox_url}/v1/file/write",
                    json={"file": path, "content": content},
                    timeout=10.0
                )
                return resp.json()
            except Exception as e:
                return {"error": str(e)}

    async def _create_agent_card(self) -> Dict[str, Any]:
        """Create ERC-8004 agent card."""
        from ..agent.agent_card import create_tee_agent_card

        agent_address = await self._get_agent_address()

        capabilities = [
            ("shell-execution", "Execute shell commands via AIO Sandbox"),
            ("file-operations", "Read/write files in sandbox"),
            ("browser-control", "Control browser via CDP"),
            ("jupyter-execution", "Run Python/Node.js code")
        ]

        return create_tee_agent_card(
            name=f"TEE Server Agent - {self.config.domain}",
            description="TEE-secured agent with AIO Sandbox integration for secure code execution",
            domain=self.config.domain,
            agent_address=agent_address,
            agent_id=self.agent_id if self.is_registered else None,
            signature=None,
            capabilities=capabilities,
            chain_id=self.config.chain_id
        )
