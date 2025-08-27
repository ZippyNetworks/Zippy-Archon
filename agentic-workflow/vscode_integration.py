# vscode_integration.py

"""
VS Code Integration for ZippyTrust & ZippyCoin

This module provides integration with VS Code for:
- Plugin development and testing
- Trust verification in real-time
- Marketplace integration
- Multi-agent workflow orchestration
"""

import json
import asyncio
import websockets
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from datetime import datetime
import logging

from plugins.trust_manager import ZippyTrustManager, PluginMetadata
from plugins.secure_plugin_manager import SecurePluginManager
from plugins.marketplace import ZippyCoinMarketplace

logger = logging.getLogger(__name__)

class VSCodeIntegration:
    """
    VS Code integration for ZippyTrust and ZippyCoin ecosystem.
    
    Provides real-time plugin development, testing, and marketplace integration
    directly within VS Code.
    """
    
    def __init__(self, workspace_path: str = None):
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self.trust_manager = ZippyTrustManager()
        self.secure_manager = SecurePluginManager()
        self.marketplace = ZippyCoinMarketplace()
        self.websocket_server = None
        self.clients = set()
        self.plugin_watchers = {}
        
    async def start_server(self, host: str = "localhost", port: int = 8765):
        """Start the VS Code integration WebSocket server"""
        try:
            self.websocket_server = await websockets.serve(
                self.handle_client, host, port
            )
            logger.info(f"VS Code integration server started on ws://{host}:{port}")
            
            # Start plugin watching
            await self.start_plugin_watchers()
            
            await self.websocket_server.wait_closed()
        except Exception as e:
            logger.error(f"Failed to start VS Code integration server: {e}")
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connections"""
        self.clients.add(websocket)
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
    
    async def process_message(self, websocket, message: str):
        """Process incoming WebSocket messages"""
        try:
            data = json.loads(message)
            command = data.get("command")
            
            if command == "verify_plugin":
                await self.handle_verify_plugin(websocket, data)
            elif command == "list_plugins":
                await self.handle_list_plugins(websocket, data)
            elif command == "purchase_plugin":
                await self.handle_purchase_plugin(websocket, data)
            elif command == "create_plugin":
                await self.handle_create_plugin(websocket, data)
            elif command == "test_plugin":
                await self.handle_test_plugin(websocket, data)
            elif command == "deploy_plugin":
                await self.handle_deploy_plugin(websocket, data)
            else:
                await websocket.send(json.dumps({
                    "error": f"Unknown command: {command}"
                }))
                
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "error": "Invalid JSON message"
            }))
        except Exception as e:
            await websocket.send(json.dumps({
                "error": f"Processing error: {str(e)}"
            }))
    
    async def handle_verify_plugin(self, websocket, data: Dict[str, Any]):
        """Handle plugin verification request"""
        try:
            plugin_path = data.get("plugin_path")
            if not plugin_path:
                raise ValueError("Plugin path is required")
            
            # Read plugin code
            plugin_file = Path(plugin_path)
            if not plugin_file.exists():
                raise FileNotFoundError(f"Plugin file not found: {plugin_path}")
            
            plugin_code = plugin_file.read_text()
            
            # Extract metadata from plugin
            metadata = self.extract_plugin_metadata(plugin_code, plugin_file.name)
            
            # Verify plugin
            trust_score = await self.trust_manager.verify_plugin(plugin_code, metadata)
            
            # Send verification result
            await websocket.send(json.dumps({
                "type": "verification_result",
                "plugin_path": plugin_path,
                "trust_score": trust_score.zippy_trust_score,
                "verification_status": trust_score.verification_status,
                "details": {
                    "code_quality": trust_score.code_quality_score,
                    "security_checks": trust_score.security_checks,
                    "audit_trail": trust_score.audit_trail
                }
            }))
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "error": str(e)
            }))
    
    async def handle_list_plugins(self, websocket, data: Dict[str, Any]):
        """Handle plugin listing request"""
        try:
            query = data.get("query", "")
            min_trust = data.get("min_trust", 0.0)
            max_price = data.get("max_price", None)
            
            plugins = self.marketplace.search_plugins(
                query=query,
                min_trust=min_trust,
                max_price=max_price
            )
            
            plugin_list = []
            for plugin in plugins:
                plugin_list.append({
                    "id": plugin.plugin_id,
                    "name": plugin.name,
                    "description": plugin.description,
                    "author": plugin.author,
                    "price": plugin.price_zippycoin,
                    "trust_score": plugin.trust_score,
                    "rating": plugin.rating,
                    "downloads": plugin.download_count,
                    "tags": plugin.tags
                })
            
            await websocket.send(json.dumps({
                "type": "plugin_list",
                "plugins": plugin_list,
                "count": len(plugin_list)
            }))
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "error": str(e)
            }))
    
    async def handle_purchase_plugin(self, websocket, data: Dict[str, Any]):
        """Handle plugin purchase request"""
        try:
            plugin_id = data.get("plugin_id")
            wallet_address = data.get("wallet_address")
            
            if not plugin_id or not wallet_address:
                raise ValueError("Plugin ID and wallet address are required")
            
            result = await self.marketplace.purchase_plugin(plugin_id, wallet_address)
            
            await websocket.send(json.dumps({
                "type": "purchase_result",
                "success": result["success"],
                "message": result.get("message", ""),
                "error": result.get("error", ""),
                "transaction": result.get("transaction", {})
            }))
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "error": str(e)
            }))
    
    async def handle_create_plugin(self, websocket, data: Dict[str, Any]):
        """Handle plugin creation request"""
        try:
            plugin_name = data.get("name")
            description = data.get("description", "")
            author = data.get("author", "unknown")
            tags = data.get("tags", [])
            
            if not plugin_name:
                raise ValueError("Plugin name is required")
            
            # Create plugin template
            plugin_code = self.generate_plugin_template(
                name=plugin_name,
                description=description,
                author=author,
                tags=tags
            )
            
            # Save plugin file
            plugin_file = self.workspace_path / "plugins" / f"{plugin_name}.py"
            plugin_file.parent.mkdir(exist_ok=True)
            plugin_file.write_text(plugin_code)
            
            await websocket.send(json.dumps({
                "type": "plugin_created",
                "plugin_path": str(plugin_file),
                "plugin_code": plugin_code
            }))
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "error": str(e)
            }))
    
    async def handle_test_plugin(self, websocket, data: Dict[str, Any]):
        """Handle plugin testing request"""
        try:
            plugin_path = data.get("plugin_path")
            test_data = data.get("test_data", {})
            
            if not plugin_path:
                raise ValueError("Plugin path is required")
            
            # Load and test plugin
            test_result = await self.test_plugin(plugin_path, test_data)
            
            await websocket.send(json.dumps({
                "type": "test_result",
                "plugin_path": plugin_path,
                "success": test_result["success"],
                "result": test_result.get("result", {}),
                "error": test_result.get("error", ""),
                "execution_time": test_result.get("execution_time", 0)
            }))
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "error": str(e)
            }))
    
    async def handle_deploy_plugin(self, websocket, data: Dict[str, Any]):
        """Handle plugin deployment to marketplace"""
        try:
            plugin_path = data.get("plugin_path")
            price = data.get("price", 0.0)
            wallet_address = data.get("wallet_address")
            
            if not plugin_path or not wallet_address:
                raise ValueError("Plugin path and wallet address are required")
            
            # Create marketplace listing
            listing = await self.create_marketplace_listing(
                plugin_path, price, wallet_address
            )
            
            # Deploy to marketplace
            success = await self.marketplace.list_plugin(listing, wallet_address)
            
            await websocket.send(json.dumps({
                "type": "deploy_result",
                "success": success,
                "plugin_id": listing.plugin_id,
                "message": "Plugin deployed successfully" if success else "Deployment failed"
            }))
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "error": str(e)
            }))
    
    def extract_plugin_metadata(self, plugin_code: str, filename: str) -> PluginMetadata:
        """Extract metadata from plugin code"""
        # Simple metadata extraction - in a real implementation, you'd use AST parsing
        lines = plugin_code.split('\n')
        
        name = filename.replace('.py', '')
        description = "No description provided"
        author = "unknown"
        version = "1.0.0"
        dependencies = []
        tags = []
        license = "MIT"
        
        for line in lines:
            line = line.strip()
            if line.startswith('name ='):
                name = line.split('=')[1].strip().strip('"\'')
            elif line.startswith('description ='):
                description = line.split('=')[1].strip().strip('"\'')
            elif line.startswith('author ='):
                author = line.split('=')[1].strip().strip('"\'')
            elif line.startswith('version ='):
                version = line.split('=')[1].strip().strip('"\'')
            elif line.startswith('dependencies ='):
                # Parse list format
                deps_str = line.split('=')[1].strip()
                if deps_str.startswith('[') and deps_str.endswith(']'):
                    dependencies = [d.strip().strip('"\'') for d in deps_str[1:-1].split(',')]
            elif line.startswith('tags ='):
                # Parse list format
                tags_str = line.split('=')[1].strip()
                if tags_str.startswith('[') and tags_str.endswith(']'):
                    tags = [t.strip().strip('"\'') for t in tags_str[1:-1].split(',')]
            elif line.startswith('license ='):
                license = line.split('=')[1].strip().strip('"\'')
        
        return PluginMetadata(
            name=name,
            description=description,
            author=author,
            version=version,
            dependencies=dependencies,
            tags=tags,
            license=license
        )
    
    def generate_plugin_template(self, name: str, description: str, author: str, tags: List[str]) -> str:
        """Generate a plugin template with ZippyTrust best practices"""
        template = f'''"""
{name} - {description}

This plugin follows ZippyTrust best practices for security and code quality.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import hashlib

# Configure logging
logger = logging.getLogger(__name__)

class {name.replace('_', '').title()}Plugin:
    """
    {description}
    
    This plugin demonstrates ZippyTrust best practices:
    - Proper documentation and type hints
    - Error handling and logging
    - Security-conscious code
    - Audit trail for operations
    """
    
    # Plugin metadata
    name = "{name}"
    description = "{description}"
    author = "{author}"
    version = "1.0.0"
    dependencies = ["logging", "json", "hashlib"]
    tags = {tags}
    license = "MIT"
    repository = None
    
    def __init__(self):
        """Initialize the plugin with proper error handling."""
        try:
            self.initialized = True
            self.created_at = datetime.now().isoformat()
            logger.info(f"{name}Plugin initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize {name}Plugin: {{e}}")
            self.initialized = False
    
    def run(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Execute the plugin with proper validation and error handling.
        
        Args:
            input_data: Input data dictionary
            **kwargs: Additional keyword arguments
            
        Returns:
            Dict containing the result and metadata
        """
        try:
            # Input validation
            if not isinstance(input_data, dict):
                raise ValueError("Input data must be a dictionary")
            
            # Log the execution
            logger.info(f"{name}Plugin executing with input: {{input_data}}")
            
            # Process the input data safely
            result = self._process_data_safely(input_data)
            
            # Create audit trail
            audit_entry = {{
                "timestamp": datetime.now().isoformat(),
                "action": "plugin_execution",
                "input_hash": self._hash_data(input_data),
                "result_hash": self._hash_data(result),
                "status": "success"
            }}
            
            # Return structured result
            return {{
                "success": True,
                "result": result,
                "metadata": {{
                    "plugin_name": self.name,
                    "version": self.version,
                    "execution_time": datetime.now().isoformat(),
                    "audit_trail": [audit_entry]
                }}
            }}
            
        except ValueError as e:
            logger.error(f"Input validation error: {{e}}")
            return {{
                "success": False,
                "error": f"Input validation failed: {{e}}",
                "error_type": "validation_error"
            }}
        except Exception as e:
            logger.error(f"Plugin execution error: {{e}}")
            return {{
                "success": False,
                "error": f"Plugin execution failed: {{e}}",
                "error_type": "execution_error"
            }}
    
    def _process_data_safely(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data with security checks.
        
        Args:
            data: Input data to process
            
        Returns:
            Processed data
        """
        # Security check: Look for potentially dangerous patterns
        data_str = json.dumps(data, default=str)
        
        dangerous_patterns = [
            "eval(", "exec(", "os.system(", "subprocess.call(",
            "pickle.loads(", "marshal.loads(", "yaml.load("
        ]
        
        for pattern in dangerous_patterns:
            if pattern in data_str:
                raise ValueError(f"Input contains potentially dangerous pattern: {{pattern}}")
        
        # Safe data processing
        processed_data = {{
            "original_input": data,
            "processed_at": datetime.now().isoformat(),
            "input_size": len(data_str),
            "checksum": self._hash_data(data),
            "status": "processed_safely"
        }}
        
        # Add your custom processing logic here
        # Example: process text data
        if "text" in data:
            processed_data["word_count"] = len(data["text"].split())
            processed_data["character_count"] = len(data["text"])
        
        # Example: process numeric data
        if "numbers" in data and isinstance(data["numbers"], list):
            processed_data["sum"] = sum(data["numbers"])
            processed_data["average"] = sum(data["numbers"]) / len(data["numbers"])
        
        return processed_data
    
    def _hash_data(self, data: Any) -> str:
        """
        Create a secure hash of data for audit purposes.
        
        Args:
            data: Data to hash
            
        Returns:
            SHA-256 hash of the data
        """
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.sha256(data_str.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to hash data: {{e}}")
            return "hash_failed"
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the plugin.
        
        Returns:
            Health check results
        """
        try:
            # Test basic functionality
            test_input = {{"test": "data", "numbers": [1, 2, 3, 4, 5]}}
            result = self.run(test_input)
            
            return {{
                "status": "healthy" if result["success"] else "unhealthy",
                "initialized": self.initialized,
                "test_result": result,
                "timestamp": datetime.now().isoformat()
            }}
        except Exception as e:
            return {{
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }}
'''
        return template
    
    async def test_plugin(self, plugin_path: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a plugin with given test data"""
        try:
            start_time = datetime.now()
            
            # Import and instantiate plugin
            import importlib.util
            spec = importlib.util.spec_from_file_location("plugin", plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class
            plugin_class = None
            for name, obj in module.__dict__.items():
                if hasattr(obj, 'name') and hasattr(obj, 'run'):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                raise ValueError("No valid plugin class found")
            
            # Instantiate and test
            plugin_instance = plugin_class()
            result = plugin_instance.run(test_data)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            return {
                "success": result.get("success", False),
                "result": result.get("result", {}),
                "error": result.get("error", ""),
                "execution_time": execution_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": 0
            }
    
    async def create_marketplace_listing(self, plugin_path: str, price: float, wallet_address: str):
        """Create a marketplace listing for a plugin"""
        from plugins.marketplace import PluginListing
        
        # Extract plugin information
        plugin_file = Path(plugin_path)
        plugin_code = plugin_file.read_text()
        metadata = self.extract_plugin_metadata(plugin_code, plugin_file.name)
        
        # Verify plugin first
        trust_score = await self.trust_manager.verify_plugin(plugin_code, metadata)
        
        # Create listing
        listing = PluginListing(
            plugin_id=metadata.name,
            name=metadata.name,
            description=metadata.description,
            author=wallet_address,
            price_zippycoin=price,
            trust_score=trust_score.zippy_trust_score,
            download_count=0,
            rating=0.0,
            tags=metadata.tags,
            version=metadata.version,
            license=metadata.license,
            repository=metadata.repository
        )
        
        return listing
    
    async def start_plugin_watchers(self):
        """Start watching for plugin file changes"""
        plugins_dir = self.workspace_path / "plugins"
        if plugins_dir.exists():
            logger.info(f"Starting plugin watchers for {plugins_dir}")
            # In a real implementation, you'd use a file watcher library
            # For now, we'll just log that we're ready to watch
    
    async def broadcast_to_clients(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.clients:
            return
        
        message_str = json.dumps(message)
        await asyncio.gather(
            *[client.send(message_str) for client in self.clients],
            return_exceptions=True
        )

# VS Code Extension Integration
class VSCodeExtension:
    """
    VS Code extension integration for the ZippyTrust ecosystem.
    
    This class provides the interface that the VS Code extension would use
    to communicate with the ZippyTrust system.
    """
    
    def __init__(self):
        self.integration = VSCodeIntegration()
        self.command_handlers = {
            "verify": self.verify_plugin,
            "test": self.test_plugin,
            "deploy": self.deploy_plugin,
            "purchase": self.purchase_plugin,
            "list": self.list_plugins
        }
    
    async def handle_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle VS Code extension commands"""
        if command not in self.command_handlers:
            return {"error": f"Unknown command: {command}"}
        
        try:
            return await self.command_handlers[command](params)
        except Exception as e:
            return {"error": str(e)}
    
    async def verify_plugin(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a plugin"""
        plugin_path = params.get("plugin_path")
        if not plugin_path:
            return {"error": "Plugin path is required"}
        
        plugin_code = Path(plugin_path).read_text()
        metadata = self.integration.extract_plugin_metadata(plugin_code, Path(plugin_path).name)
        trust_score = await self.integration.trust_manager.verify_plugin(plugin_code, metadata)
        
        return {
            "trust_score": trust_score.zippy_trust_score,
            "status": trust_score.verification_status,
            "details": {
                "code_quality": trust_score.code_quality_score,
                "security_checks": trust_score.security_checks
            }
        }
    
    async def test_plugin(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Test a plugin"""
        plugin_path = params.get("plugin_path")
        test_data = params.get("test_data", {})
        
        if not plugin_path:
            return {"error": "Plugin path is required"}
        
        return await self.integration.test_plugin(plugin_path, test_data)
    
    async def deploy_plugin(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a plugin to marketplace"""
        plugin_path = params.get("plugin_path")
        price = params.get("price", 0.0)
        wallet_address = params.get("wallet_address")
        
        if not all([plugin_path, wallet_address]):
            return {"error": "Plugin path and wallet address are required"}
        
        listing = await self.integration.create_marketplace_listing(
            plugin_path, price, wallet_address
        )
        success = await self.integration.marketplace.list_plugin(listing, wallet_address)
        
        return {
            "success": success,
            "plugin_id": listing.plugin_id,
            "message": "Plugin deployed successfully" if success else "Deployment failed"
        }
    
    async def purchase_plugin(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Purchase a plugin"""
        plugin_id = params.get("plugin_id")
        wallet_address = params.get("wallet_address")
        
        if not all([plugin_id, wallet_address]):
            return {"error": "Plugin ID and wallet address are required"}
        
        return await self.integration.marketplace.purchase_plugin(plugin_id, wallet_address)
    
    async def list_plugins(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available plugins"""
        query = params.get("query", "")
        min_trust = params.get("min_trust", 0.0)
        max_price = params.get("max_price", None)
        
        plugins = self.integration.marketplace.search_plugins(
            query=query,
            min_trust=min_trust,
            max_price=max_price
        )
        
        return {
            "plugins": [
                {
                    "id": p.plugin_id,
                    "name": p.name,
                    "description": p.description,
                    "price": p.price_zippycoin,
                    "trust_score": p.trust_score
                }
                for p in plugins
            ]
        }

# Multi-Agent Workflow Orchestrator
class MultiAgentOrchestrator:
    """
    Multi-agent workflow orchestrator for VS Code integration.
    
    This orchestrator manages multiple AI agents working on different aspects
    of plugin development, testing, and deployment.
    """
    
    def __init__(self):
        self.agents = {}
        self.workflows = {}
        self.vscode_integration = VSCodeIntegration()
    
    async def create_workflow(self, workflow_id: str, agents: List[str], steps: List[Dict[str, Any]]):
        """Create a new multi-agent workflow"""
        self.workflows[workflow_id] = {
            "agents": agents,
            "steps": steps,
            "status": "created",
            "current_step": 0,
            "results": {}
        }
        
        logger.info(f"Created workflow {workflow_id} with {len(agents)} agents")
    
    async def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any]):
        """Execute a multi-agent workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        workflow["status"] = "running"
        workflow["input_data"] = input_data
        
        try:
            for i, step in enumerate(workflow["steps"]):
                workflow["current_step"] = i
                
                # Execute step with appropriate agent
                agent_name = step.get("agent")
                if agent_name and agent_name in self.agents:
                    result = await self.agents[agent_name].execute(step, input_data)
                    workflow["results"][f"step_{i}"] = result
                
                # Handle step-specific actions
                action = step.get("action")
                if action == "verify_plugin":
                    await self.handle_plugin_verification(step, input_data)
                elif action == "test_plugin":
                    await self.handle_plugin_testing(step, input_data)
                elif action == "deploy_plugin":
                    await self.handle_plugin_deployment(step, input_data)
            
            workflow["status"] = "completed"
            return workflow["results"]
            
        except Exception as e:
            workflow["status"] = "failed"
            workflow["error"] = str(e)
            raise
    
    async def handle_plugin_verification(self, step: Dict[str, Any], input_data: Dict[str, Any]):
        """Handle plugin verification in workflow"""
        plugin_path = step.get("plugin_path") or input_data.get("plugin_path")
        if plugin_path:
            # Trigger verification through VS Code integration
            await self.vscode_integration.broadcast_to_clients({
                "type": "workflow_step",
                "action": "verify_plugin",
                "plugin_path": plugin_path
            })
    
    async def handle_plugin_testing(self, step: Dict[str, Any], input_data: Dict[str, Any]):
        """Handle plugin testing in workflow"""
        plugin_path = step.get("plugin_path") or input_data.get("plugin_path")
        test_data = step.get("test_data", {})
        
        if plugin_path:
            # Trigger testing through VS Code integration
            await self.vscode_integration.broadcast_to_clients({
                "type": "workflow_step",
                "action": "test_plugin",
                "plugin_path": plugin_path,
                "test_data": test_data
            })
    
    async def handle_plugin_deployment(self, step: Dict[str, Any], input_data: Dict[str, Any]):
        """Handle plugin deployment in workflow"""
        plugin_path = step.get("plugin_path") or input_data.get("plugin_path")
        price = step.get("price", 0.0)
        wallet_address = step.get("wallet_address") or input_data.get("wallet_address")
        
        if all([plugin_path, wallet_address]):
            # Trigger deployment through VS Code integration
            await self.vscode_integration.broadcast_to_clients({
                "type": "workflow_step",
                "action": "deploy_plugin",
                "plugin_path": plugin_path,
                "price": price,
                "wallet_address": wallet_address
            })

# Main entry point for VS Code integration
async def main():
    """Main entry point for VS Code integration server"""
    integration = VSCodeIntegration()
    
    print("🚀 Starting VS Code Integration Server...")
    print("📡 WebSocket server will be available at ws://localhost:8765")
    print("🔌 Connect your VS Code extension to start developing plugins!")
    
    await integration.start_server()

if __name__ == "__main__":
    asyncio.run(main())
