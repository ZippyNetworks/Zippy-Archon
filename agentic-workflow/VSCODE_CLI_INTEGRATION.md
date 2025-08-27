# 🔌 VS Code Integration & 🖥️ CLI Tools

This document describes the VS Code integration and command-line interface tools for the ZippyTrust and ZippyCoin ecosystem.

## Overview

The VS Code integration and CLI tools provide:

- **🔌 Real-time VS Code Integration**: WebSocket-based communication for plugin development
- **🖥️ Comprehensive CLI**: Command-line tools for all ecosystem operations
- **🔄 Multi-Agent Workflows**: Orchestrated plugin development and deployment
- **📊 Development Analytics**: Real-time feedback and reporting

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   VS Code       │    │   WebSocket     │    │   ZippyTrust    │
│   Extension     │◄──►│   Server        │◄──►│   Ecosystem     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Tools     │    │   Multi-Agent   │    │   Marketplace   │
│                 │    │   Orchestrator  │    │   Integration   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## VS Code Integration

### WebSocket Server

The VS Code integration provides a WebSocket server that enables real-time communication between VS Code extensions and the ZippyTrust ecosystem.

#### Starting the Server

```bash
# Start the integration server
python vscode_integration.py

# Or use the CLI
python zippy_cli.py vscode server --host localhost --port 8765
```

#### WebSocket Commands

The server accepts the following commands:

```json
{
  "command": "verify_plugin",
  "plugin_path": "/path/to/plugin.py"
}
```

```json
{
  "command": "list_plugins",
  "query": "utility",
  "min_trust": 0.8,
  "max_price": 50.0
}
```

```json
{
  "command": "purchase_plugin",
  "plugin_id": "my_plugin",
  "wallet_address": "zippy_wallet_123"
}
```

```json
{
  "command": "create_plugin",
  "name": "my_plugin",
  "description": "A useful plugin",
  "author": "developer",
  "tags": ["utility", "demo"]
}
```

```json
{
  "command": "test_plugin",
  "plugin_path": "/path/to/plugin.py",
  "test_data": {"text": "test", "numbers": [1, 2, 3]}
}
```

```json
{
  "command": "deploy_plugin",
  "plugin_path": "/path/to/plugin.py",
  "price": 10.0,
  "wallet_address": "zippy_wallet_123"
}
```

### Plugin Template Generation

The VS Code integration automatically generates plugin templates that follow ZippyTrust best practices:

```python
"""
my_plugin - A useful plugin

This plugin follows ZippyTrust best practices for security and code quality.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import hashlib

# Configure logging
logger = logging.getLogger(__name__)

class MyPluginPlugin:
    """
    A useful plugin
    
    This plugin demonstrates ZippyTrust best practices:
    - Proper documentation and type hints
    - Error handling and logging
    - Security-conscious code
    - Audit trail for operations
    """
    
    # Plugin metadata
    name = "my_plugin"
    description = "A useful plugin"
    author = "developer"
    version = "1.0.0"
    dependencies = ["logging", "json", "hashlib"]
    tags = ["utility", "demo"]
    license = "MIT"
    repository = None
    
    def __init__(self):
        """Initialize the plugin with proper error handling."""
        try:
            self.initialized = True
            self.created_at = datetime.now().isoformat()
            logger.info("MyPluginPlugin initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MyPluginPlugin: {e}")
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
            logger.info(f"MyPluginPlugin executing with input: {input_data}")
            
            # Process the input data safely
            result = self._process_data_safely(input_data)
            
            # Create audit trail
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": "plugin_execution",
                "input_hash": self._hash_data(input_data),
                "result_hash": self._hash_data(result),
                "status": "success"
            }
            
            # Return structured result
            return {
                "success": True,
                "result": result,
                "metadata": {
                    "plugin_name": self.name,
                    "version": self.version,
                    "execution_time": datetime.now().isoformat(),
                    "audit_trail": [audit_entry]
                }
            }
            
        except ValueError as e:
            logger.error(f"Input validation error: {e}")
            return {
                "success": False,
                "error": f"Input validation failed: {e}",
                "error_type": "validation_error"
            }
        except Exception as e:
            logger.error(f"Plugin execution error: {e}")
            return {
                "success": False,
                "error": f"Plugin execution failed: {e}",
                "error_type": "execution_error"
            }
    
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
                raise ValueError(f"Input contains potentially dangerous pattern: {pattern}")
        
        # Safe data processing
        processed_data = {
            "original_input": data,
            "processed_at": datetime.now().isoformat(),
            "input_size": len(data_str),
            "checksum": self._hash_data(data),
            "status": "processed_safely"
        }
        
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
            logger.warning(f"Failed to hash data: {e}")
            return "hash_failed"
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the plugin.
        
        Returns:
            Health check results
        """
        try:
            # Test basic functionality
            test_input = {"test": "data", "numbers": [1, 2, 3, 4, 5]}
            result = self.run(test_input)
            
            return {
                "status": "healthy" if result["success"] else "unhealthy",
                "initialized": self.initialized,
                "test_result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
```

## Command Line Interface

The ZippyTrust CLI provides comprehensive command-line tools for managing the ecosystem.

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Make CLI executable
chmod +x zippy_cli.py
```

### Basic Usage

```bash
# Show help
python zippy_cli.py --help

# Show version
python zippy_cli.py --version

# Check system status
python zippy_cli.py status
```

### Trust Management

```bash
# Verify a plugin
python zippy_cli.py trust verify plugins/my_plugin.py

# Verify with detailed output
python zippy_cli.py trust verify plugins/my_plugin.py --output results.json

# List trusted plugins
python zippy_cli.py trust list

# List with custom threshold
python zippy_cli.py trust list --min-score 0.8

# List in different formats
python zippy_cli.py trust list --format json
python zippy_cli.py trust list --format csv

# Update trust score manually
python zippy_cli.py trust update my_plugin 0.9 "Manual review completed"
```

### Marketplace Operations

```bash
# Search for plugins
python zippy_cli.py marketplace search

# Search with filters
python zippy_cli.py marketplace search --query "utility" --min-trust 0.8 --max-price 50

# Search by tags
python zippy_cli.py marketplace search --tags "utility,demo,trusted"

# Purchase a plugin
python zippy_cli.py marketplace purchase my_plugin zippy_wallet_123

# Check wallet balance
python zippy_cli.py marketplace balance zippy_wallet_123

# View purchase history
python zippy_cli.py marketplace history zippy_wallet_123
```

### Plugin Development

```bash
# Create a new plugin
python zippy_cli.py plugin create my_plugin --description "A useful plugin" --author "developer" --tags "utility,demo"

# Create with custom output directory
python zippy_cli.py plugin create my_plugin --output ./my_plugins

# Test a plugin
python zippy_cli.py plugin test plugins/my_plugin.py

# Test with custom data
python zippy_cli.py plugin test plugins/my_plugin.py --test-data '{"text": "hello", "numbers": [1,2,3]}'

# Deploy a plugin to marketplace
python zippy_cli.py plugin deploy plugins/my_plugin.py 10.0 zippy_wallet_123
```

### VS Code Integration

```bash
# Start VS Code integration server
python zippy_cli.py vscode server

# Start with custom host/port
python zippy_cli.py vscode server --host 0.0.0.0 --port 9000

# Execute a workflow
python zippy_cli.py vscode workflow my_workflow workflow.json
```

### System Utilities

```bash
# Generate system report
python zippy_cli.py report

# Generate report with output file
python zippy_cli.py report --output system_report.json
```

## Multi-Agent Workflows

The system supports orchestrated multi-agent workflows for plugin development and deployment.

### Workflow Definition

Workflows are defined in JSON format:

```json
{
  "workflow_id": "plugin_development_workflow",
  "name": "Plugin Development and Deployment Workflow",
  "description": "A comprehensive workflow for developing, testing, and deploying plugins",
  "version": "1.0.0",
  "agents": [
    "code_analyzer",
    "security_checker", 
    "test_runner",
    "deployment_manager"
  ],
  "steps": [
    {
      "step_id": "code_analysis",
      "name": "Code Quality Analysis",
      "agent": "code_analyzer",
      "action": "analyze_code",
      "description": "Analyze plugin code for quality metrics",
      "parameters": {
        "metrics": ["complexity", "documentation", "type_hints", "error_handling"]
      }
    },
    {
      "step_id": "security_verification",
      "name": "Security Verification",
      "agent": "security_checker", 
      "action": "verify_plugin",
      "description": "Verify plugin security and trust score",
      "parameters": {
        "security_checks": ["dangerous_functions", "hardcoded_secrets", "network_access", "file_access"]
      }
    },
    {
      "step_id": "testing",
      "name": "Plugin Testing",
      "agent": "test_runner",
      "action": "test_plugin",
      "description": "Run comprehensive tests on the plugin",
      "parameters": {
        "test_data": {
          "text": "Sample text for testing",
          "numbers": [1, 2, 3, 4, 5],
          "nested": {"key": "value"}
        },
        "test_cases": ["basic_functionality", "error_handling", "edge_cases"]
      }
    },
    {
      "step_id": "marketplace_deployment",
      "name": "Marketplace Deployment",
      "agent": "deployment_manager",
      "action": "deploy_plugin",
      "description": "Deploy plugin to ZippyCoin marketplace",
      "parameters": {
        "price": 10.0,
        "auto_verify": true,
        "publish_immediately": false
      }
    }
  ],
  "input_data": {
    "plugin_path": "./plugins/my_plugin.py",
    "wallet_address": "zippy_wallet_123456789",
    "author": "trusted_developer",
    "tags": ["utility", "demo", "trusted"]
  },
  "error_handling": {
    "retry_attempts": 3,
    "retry_delay": 5,
    "fail_fast": false,
    "rollback_on_failure": true
  },
  "notifications": {
    "email": "developer@example.com",
    "webhook_url": "https://api.example.com/webhooks/workflow",
    "slack_channel": "#plugin-deployments"
  }
}
```

### Workflow Execution

```bash
# Execute a workflow
python zippy_cli.py vscode workflow my_workflow workflow.json

# Monitor workflow progress
python zippy_cli.py vscode workflow status my_workflow
```

## VS Code Extension Development

To develop a VS Code extension that integrates with this system:

### Extension Structure

```typescript
// extension.ts
import * as vscode from 'vscode';
import WebSocket from 'ws';

export function activate(context: vscode.ExtensionContext) {
    const ws = new WebSocket('ws://localhost:8765');
    
    ws.on('open', () => {
        console.log('Connected to ZippyTrust server');
    });
    
    ws.on('message', (data) => {
        const message = JSON.parse(data.toString());
        handleMessage(message);
    });
    
    // Register commands
    let verifyCommand = vscode.commands.registerCommand('zippytrust.verifyPlugin', () => {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            const document = editor.document;
            ws.send(JSON.stringify({
                command: 'verify_plugin',
                plugin_path: document.fileName
            }));
        }
    });
    
    let createCommand = vscode.commands.registerCommand('zippytrust.createPlugin', () => {
        vscode.window.showInputBox({
            prompt: 'Enter plugin name'
        }).then(name => {
            if (name) {
                ws.send(JSON.stringify({
                    command: 'create_plugin',
                    name: name,
                    description: 'A new plugin',
                    author: 'developer',
                    tags: ['utility']
                }));
            }
        });
    });
    
    context.subscriptions.push(verifyCommand, createCommand);
}

function handleMessage(message: any) {
    switch (message.type) {
        case 'verification_result':
            vscode.window.showInformationMessage(
                `Plugin verified! Trust score: ${message.trust_score}`
            );
            break;
        case 'plugin_created':
            vscode.window.showInformationMessage(
                `Plugin created: ${message.plugin_path}`
            );
            break;
        case 'error':
            vscode.window.showErrorMessage(`Error: ${message.error}`);
            break;
    }
}
```

### Package.json Configuration

```json
{
  "name": "zippytrust-vscode",
  "displayName": "ZippyTrust Integration",
  "description": "ZippyTrust and ZippyCoin integration for VS Code",
  "version": "0.0.1",
  "engines": {
    "vscode": "^1.60.0"
  },
  "categories": [
    "Other"
  ],
  "activationEvents": [
    "onCommand:zippytrust.verifyPlugin",
    "onCommand:zippytrust.createPlugin"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "zippytrust.verifyPlugin",
        "title": "Verify Plugin with ZippyTrust"
      },
      {
        "command": "zippytrust.createPlugin",
        "title": "Create New Plugin"
      }
    ],
    "menus": {
      "commandPalette": [
        {
          "command": "zippytrust.verifyPlugin"
        },
        {
          "command": "zippytrust.createPlugin"
        }
      ]
    }
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./"
  },
  "devDependencies": {
    "@types/vscode": "^1.60.0",
    "@types/node": "^16.0.0",
    "typescript": "^4.5.0",
    "ws": "^8.0.0"
  }
}
```

## Configuration

### Environment Variables

```bash
# VS Code Integration
VSCODE_SERVER_HOST=localhost
VSCODE_SERVER_PORT=8765

# ZippyTrust API
ZIPPYTRUST_API_URL=https://api.zippytrust.com

# ZippyCoin API
ZIPPYCOIN_API_URL=https://api.zippycoin.com

# Marketplace API
MARKETPLACE_API_URL=https://marketplace.zippycoin.com

# Trust settings
TRUST_THRESHOLD=0.7
TRUST_VERIFICATION_ENABLED=true
```

### Configuration Files

Create a `config.json` file for custom settings:

```json
{
  "vscode_integration": {
    "host": "localhost",
    "port": 8765,
    "auto_connect": true,
    "reconnect_attempts": 3
  },
  "trust_system": {
    "threshold": 0.7,
    "verification_enabled": true,
    "cache_duration": 3600
  },
  "marketplace": {
    "auto_verify": true,
    "min_trust_for_listing": 0.8,
    "max_price_limit": 1000.0
  },
  "workflows": {
    "default_timeout": 300,
    "max_retries": 3,
    "parallel_execution": true
  }
}
```

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Ensure the VS Code integration server is running
   - Check firewall settings
   - Verify host and port configuration

2. **Plugin Verification Fails**
   - Check plugin code quality
   - Review security practices
   - Ensure proper metadata

3. **CLI Commands Not Working**
   - Verify Python environment
   - Check dependencies installation
   - Ensure proper file permissions

### Debug Mode

Enable debug logging:

```bash
# Set debug environment variable
export ZIPPYTRUST_DEBUG=true

# Run CLI with debug output
python zippy_cli.py --debug status

# Start server with debug logging
python zippy_cli.py vscode server --debug
```

### Log Files

Log files are stored in:
- `logs/vscode_integration.log` - VS Code integration logs
- `logs/cli.log` - CLI operation logs
- `logs/workflow.log` - Workflow execution logs

## Future Enhancements

- **Real-time Collaboration**: Multi-user plugin development
- **Advanced Analytics**: Machine learning for code quality assessment
- **Plugin Versioning**: Git integration and version control
- **Automated Testing**: CI/CD pipeline integration
- **Plugin Marketplace UI**: Web-based marketplace interface
- **Mobile Integration**: Mobile app for marketplace browsing
- **Blockchain Integration**: Full blockchain-based trust verification

## Contributing

To contribute to the VS Code integration and CLI tools:

1. Follow the coding standards and best practices
2. Add comprehensive tests for new features
3. Update documentation for any changes
4. Ensure backward compatibility
5. Test with real VS Code extensions

## License

This integration is part of the Zippy Archon project and follows the same licensing terms.
