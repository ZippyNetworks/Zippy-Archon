# plugins/demo_trusted_plugin.py

"""
Demo Trusted Plugin - A high-quality plugin that demonstrates ZippyTrust features.

This plugin is designed to showcase:
- Proper code documentation
- Type hints
- Error handling
- Security best practices
- Clean code structure
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DemoTrustedPlugin:
    """
    A demonstration plugin that meets high trust standards.
    
    This plugin showcases best practices for:
    - Code quality
    - Security
    - Documentation
    - Error handling
    """
    
    # Plugin metadata
    name = "demo_trusted_plugin"
    description = "A high-quality demo plugin showcasing ZippyTrust best practices"
    author = "ZippyTrust Team"
    version = "1.0.0"
    dependencies = ["logging", "json", "hashlib"]
    tags = ["demo", "trusted", "example", "security"]
    license = "MIT"
    repository = "https://github.com/ZippyTrust/demo-plugins"
    
    def __init__(self):
        """Initialize the demo plugin with proper error handling."""
        try:
            self.initialized = True
            self.created_at = datetime.now().isoformat()
            logger.info("DemoTrustedPlugin initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DemoTrustedPlugin: {e}")
            self.initialized = False
    
    def run(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Execute the demo plugin with proper validation and error handling.
        
        Args:
            input_data: Input data dictionary
            **kwargs: Additional keyword arguments
            
        Returns:
            Dict containing the result and metadata
            
        Raises:
            ValueError: If input validation fails
            RuntimeError: If plugin execution fails
        """
        try:
            # Input validation
            if not isinstance(input_data, dict):
                raise ValueError("Input data must be a dictionary")
            
            # Log the execution
            logger.info(f"DemoTrustedPlugin executing with input: {input_data}")
            
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
            
        Raises:
            ValueError: If data contains unsafe content
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
        
        # Add some demo processing
        if "text" in data:
            processed_data["word_count"] = len(data["text"].split())
            processed_data["character_count"] = len(data["text"])
        
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
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """
        Get comprehensive plugin information for trust verification.
        
        Returns:
            Dictionary containing plugin metadata and trust information
        """
        return {
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "version": self.version,
            "dependencies": self.dependencies,
            "tags": self.tags,
            "license": self.license,
            "repository": self.repository,
            "created_at": self.created_at,
            "trust_features": {
                "has_documentation": True,
                "has_type_hints": True,
                "has_error_handling": True,
                "has_logging": True,
                "has_security_checks": True,
                "has_audit_trail": True,
                "no_dangerous_functions": True
            }
        }
    
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

# Create a demo function plugin as well
def demo_function_plugin(input_text: str, **kwargs) -> Dict[str, Any]:
    """
    A simple function-based plugin that demonstrates trust features.
    
    Args:
        input_text: Text to process
        **kwargs: Additional arguments
        
    Returns:
        Processing result
    """
    # Plugin metadata
    demo_function_plugin.name = "demo_function_plugin"
    demo_function_plugin.description = "A simple function-based demo plugin"
    demo_function_plugin.author = "ZippyTrust Team"
    demo_function_plugin.version = "1.0.0"
    demo_function_plugin.dependencies = []
    demo_function_plugin.tags = ["demo", "function", "simple"]
    demo_function_plugin.license = "MIT"
    demo_function_plugin.repository = "https://github.com/ZippyTrust/demo-plugins"
    
    try:
        # Input validation
        if not isinstance(input_text, str):
            raise ValueError("Input must be a string")
        
        # Safe processing
        result = {
            "original_text": input_text,
            "length": len(input_text),
            "word_count": len(input_text.split()),
            "processed_at": datetime.now().isoformat(),
            "checksum": hashlib.sha256(input_text.encode()).hexdigest()
        }
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Example of a plugin that would fail trust verification
class DemoUnsafePlugin:
    """
    WARNING: This plugin demonstrates unsafe practices that would fail trust verification.
    DO NOT USE IN PRODUCTION!
    """
    
    name = "demo_unsafe_plugin"
    description = "A demo plugin that would fail trust verification"
    author = "Demo Author"
    version = "1.0.0"
    
    def run(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        WARNING: This method contains unsafe practices!
        """
        # This would fail security checks
        import os
        result = os.system(command)  # DANGEROUS!
        
        return {
            "success": True,
            "result": f"Executed: {command}",
            "return_code": result
        }

# Example of a plugin with hardcoded secrets (would fail trust verification)
class DemoSecretPlugin:
    """
    WARNING: This plugin demonstrates hardcoded secrets that would fail trust verification.
    DO NOT USE IN PRODUCTION!
    """
    
    name = "demo_secret_plugin"
    description = "A demo plugin with hardcoded secrets"
    author = "Demo Author"
    version = "1.0.0"
    
    # These would fail security checks
    API_KEY = "sk-1234567890abcdef"  # DANGEROUS!
    PASSWORD = "secretpassword123"    # DANGEROUS!
    
    def run(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        WARNING: This method contains hardcoded secrets!
        """
        return {
            "success": True,
            "result": f"Processed with API key: {self.API_KEY[:8]}...",
            "data": data
        }
