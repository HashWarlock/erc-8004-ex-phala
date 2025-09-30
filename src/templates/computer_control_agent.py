"""
Computer Control Agent

TEE-secured agent that can control computer operations via sandbox API.
Integrates ERC-8004 agent protocol with aio-sandbox for system control.
"""

from typing import Dict, Any, Optional, List
from ..agent.base import BaseAgent, AgentConfig, RegistryAddresses
import logging

logger = logging.getLogger(__name__)


class ComputerControlAgent(BaseAgent):
    """
    Agent with computer control capabilities via sandbox API.

    Capabilities:
    - Execute shell commands
    - File operations (read/write/search)
    - Code execution (Python, Node.js)
    - System monitoring
    - MCP tool integration
    """

    def __init__(
        self,
        config: AgentConfig,
        registries: RegistryAddresses,
        sandbox_url: str = "http://localhost:8080"
    ):
        super().__init__(config, registries)
        self.sandbox_url = sandbox_url
        self.sandbox_client = None
        self.session_id = f"agent-{config.domain}"

    async def initialize(self):
        """Initialize agent and sandbox client."""
        await super().initialize()

        # Import sandbox client
        try:
            from aio_sandbox import AioClient
            self.sandbox_client = AioClient(
                base_url=self.sandbox_url,
                timeout=30.0,
                retries=3,
                retry_delay=1.0
            )
            logger.info(f"Sandbox client initialized: {self.sandbox_url}")
        except ImportError:
            logger.warning("aio-sandbox not installed. Computer control disabled.")
            logger.info("Install with: pip install aio-sandbox")

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process computer control tasks.

        Task types:
        - shell: Execute shell commands
        - file_read: Read file contents
        - file_write: Write file contents
        - file_list: List directory contents
        - file_search: Search file contents
        - code_python: Execute Python code
        - code_nodejs: Execute Node.js code
        - system_info: Get system information
        """
        task_type = task_data.get("type", "unknown")

        if not self.sandbox_client:
            return {
                "task_id": task_data.get("task_id"),
                "status": "error",
                "error": "Sandbox client not initialized. Install aio-sandbox."
            }

        try:
            if task_type == "shell":
                result = await self._execute_shell(task_data)
            elif task_type == "file_read":
                result = await self._read_file(task_data)
            elif task_type == "file_write":
                result = await self._write_file(task_data)
            elif task_type == "file_list":
                result = await self._list_files(task_data)
            elif task_type == "file_search":
                result = await self._search_files(task_data)
            elif task_type == "code_python":
                result = await self._execute_python(task_data)
            elif task_type == "code_nodejs":
                result = await self._execute_nodejs(task_data)
            elif task_type == "system_info":
                result = await self._get_system_info(task_data)
            else:
                result = {
                    "status": "error",
                    "error": f"Unknown task type: {task_type}"
                }

            return {
                "task_id": task_data.get("task_id"),
                "agent_id": self.agent_id,
                "type": task_type,
                **result
            }

        except Exception as e:
            logger.error(f"Task processing failed: {e}")
            return {
                "task_id": task_data.get("task_id"),
                "status": "error",
                "error": str(e)
            }

    async def _execute_shell(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute shell command."""
        command = task_data.get("command")
        if not command:
            return {"status": "error", "error": "No command provided"}

        async_mode = task_data.get("async", False)

        result = await self.sandbox_client.shell.exec(
            command=command,
            session_id=self.session_id,
            async_mode=async_mode
        )

        if result.success:
            return {
                "status": "completed",
                "output": result.data.output if hasattr(result.data, 'output') else str(result.data),
                "exit_code": getattr(result.data, 'exit_code', 0)
            }
        else:
            return {
                "status": "error",
                "error": result.error or "Command execution failed"
            }

    async def _read_file(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Read file contents."""
        file_path = task_data.get("path")
        if not file_path:
            return {"status": "error", "error": "No file path provided"}

        result = await self.sandbox_client.file.read(file=file_path)

        if result.success:
            return {
                "status": "completed",
                "content": result.data.content if hasattr(result.data, 'content') else str(result.data),
                "path": file_path
            }
        else:
            return {
                "status": "error",
                "error": result.error or "File read failed"
            }

    async def _write_file(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Write file contents."""
        file_path = task_data.get("path")
        content = task_data.get("content")

        if not file_path or content is None:
            return {"status": "error", "error": "Missing path or content"}

        result = await self.sandbox_client.file.write(
            file=file_path,
            content=content
        )

        if result.success:
            return {
                "status": "completed",
                "path": file_path,
                "bytes_written": len(content)
            }
        else:
            return {
                "status": "error",
                "error": result.error or "File write failed"
            }

    async def _list_files(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """List directory contents."""
        directory = task_data.get("directory", ".")

        result = await self.sandbox_client.file.list(path=directory)

        if result.success:
            return {
                "status": "completed",
                "directory": directory,
                "files": result.data.files if hasattr(result.data, 'files') else []
            }
        else:
            return {
                "status": "error",
                "error": result.error or "Directory listing failed"
            }

    async def _search_files(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search file contents."""
        pattern = task_data.get("pattern")
        path = task_data.get("path", ".")

        if not pattern:
            return {"status": "error", "error": "No search pattern provided"}

        result = await self.sandbox_client.file.search(
            pattern=pattern,
            path=path
        )

        if result.success:
            return {
                "status": "completed",
                "pattern": pattern,
                "matches": result.data.matches if hasattr(result.data, 'matches') else []
            }
        else:
            return {
                "status": "error",
                "error": result.error or "File search failed"
            }

    async def _execute_python(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Python code."""
        code = task_data.get("code")
        if not code:
            return {"status": "error", "error": "No code provided"}

        timeout = task_data.get("timeout", 60)

        result = await self.sandbox_client.jupyter.execute(
            code=code,
            timeout=timeout
        )

        if result.success:
            return {
                "status": "completed",
                "output": result.data.output if hasattr(result.data, 'output') else str(result.data),
                "execution_time": getattr(result.data, 'execution_time', None)
            }
        else:
            return {
                "status": "error",
                "error": result.error or "Code execution failed"
            }

    async def _execute_nodejs(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Node.js code."""
        code = task_data.get("code")
        if not code:
            return {"status": "error", "error": "No code provided"}

        timeout = task_data.get("timeout", 60)

        result = await self.sandbox_client.nodejs.execute(
            code=code,
            timeout=timeout
        )

        if result.success:
            return {
                "status": "completed",
                "output": result.data.output if hasattr(result.data, 'output') else str(result.data)
            }
        else:
            return {
                "status": "error",
                "error": result.error or "Code execution failed"
            }

    async def _get_system_info(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get system information."""
        # Execute multiple commands to gather system info
        commands = {
            "os": "uname -a",
            "cpu": "cat /proc/cpuinfo | grep 'model name' | head -1",
            "memory": "free -h",
            "disk": "df -h",
            "uptime": "uptime"
        }

        info = {}
        for key, cmd in commands.items():
            try:
                result = await self.sandbox_client.shell.exec(
                    command=cmd,
                    session_id=self.session_id
                )
                if result.success:
                    info[key] = result.data.output.strip() if hasattr(result.data, 'output') else ""
            except:
                info[key] = "unavailable"

        return {
            "status": "completed",
            "system_info": info
        }

    async def _create_agent_card(self) -> Dict[str, Any]:
        """Create ERC-8004 compliant agent card."""
        from ..agent.agent_card import create_tee_agent_card

        agent_address = await self._get_agent_address()

        capabilities = [
            ("shell-execution", "Execute shell commands with security constraints"),
            ("file-operations", "Read, write, and search files on the system"),
            ("code-execution", "Run Python and Node.js code in isolated environments"),
            ("system-monitoring", "Monitor system resources and status"),
            ("file-management", "List directories and manage file systems"),
            ("computer-control", "Full computer control via sandbox API")
        ]

        card = create_tee_agent_card(
            name=f"TEE Computer Control Agent - {self.config.domain}",
            description="TEE-secured agent with computer control capabilities via sandbox API. "
                       "Can execute commands, manage files, run code, and monitor systems.",
            domain=self.config.domain,
            agent_address=agent_address,
            agent_id=self.agent_id if self.is_registered else None,
            capabilities=capabilities,
            chain_id=self.config.chain_id
        )

        # Add computer control specific metadata
        card["metadata"] = {
            "role": "computer-control",
            "sandbox_url": self.sandbox_url,
            "supported_operations": [
                "shell",
                "file_read",
                "file_write",
                "file_list",
                "file_search",
                "code_python",
                "code_nodejs",
                "system_info"
            ],
            "pricing": {
                "baseFee": "2000000000000000",  # 0.002 ETH per operation
                "currency": "ETH",
                "unit": "per-operation"
            },
            "performance": {
                "averageResponseTime": "2.5s",
                "maxConcurrentTasks": 5,
                "supportedLanguages": ["Python", "Node.js", "Bash"]
            },
            "endpoints": {
                "control": f"https://{self.config.domain}/api/control",
                "status": f"https://{self.config.domain}/api/status",
                "sandbox": self.sandbox_url
            },
            "security": {
                "tee_secured": True,
                "sandboxed": True,
                "resource_limits": True
            }
        }

        return card
