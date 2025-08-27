# plugins/secure_plugin_manager.py

import inspect
import importlib
import os
import asyncio
from typing import Protocol, Any, Dict, Optional, List
from pathlib import Path
import traceback

from .plugin_manager import Tool, TOOLS_REGISTRY
from .trust_manager import ZippyTrustManager, TrustScore, PluginMetadata

class SecurityException(Exception):
    """Raised when a plugin fails security verification"""
    pass

class PluginVerificationException(Exception):
    """Raised when plugin verification fails"""
    pass

class SecurePluginManager:
    def __init__(self, trust_threshold: float = 0.7, trust_verification: bool = True):
        self.trust_manager = ZippyTrustManager()
        self.trust_threshold = trust_threshold
        self.trust_verification = trust_verification
        self.trust_scores: Dict[str, TrustScore] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self.blocked_plugins: List[str] = []
    
    def register_tool(self, tool: Tool, metadata: Optional[PluginMetadata] = None, trust_verification: bool = None) -> bool:
        """Register tool with trust verification"""
        if trust_verification is None:
            trust_verification = self.trust_verification
        
        if trust_verification:
            try:
                # Extract plugin code for verification
                plugin_code = self._extract_plugin_code(tool)
                
                # Create metadata if not provided
                if metadata is None:
                    metadata = self._extract_metadata(tool)
                
                # Verify with ZippyTrust
                trust_score = asyncio.run(self.trust_manager.verify_plugin(plugin_code, metadata))
                
                # Store trust information
                self.trust_scores[tool.name] = trust_score
                self.plugin_metadata[tool.name] = metadata
                
                if trust_score.zippy_trust_score < self.trust_threshold:
                    self.blocked_plugins.append(tool.name)
                    raise SecurityException(
                        f"Plugin '{tool.name}' failed trust verification. "
                        f"Score: {trust_score.zippy_trust_score:.2f} "
                        f"(minimum: {self.trust_threshold})"
                    )
                
                print(f"✅ Plugin '{tool.name}' verified with trust score: {trust_score.zippy_trust_score:.2f}")
                
            except Exception as e:
                print(f"❌ Plugin '{tool.name}' verification failed: {e}")
                if isinstance(e, SecurityException):
                    raise
                else:
                    raise PluginVerificationException(f"Plugin verification failed: {e}")
        
        # Register the tool
        if tool.name in TOOLS_REGISTRY:
            print(f"⚠️  Plugin '{tool.name}' is already registered. Overwriting...")
        
        TOOLS_REGISTRY[tool.name] = tool
        return True
    
    def _extract_plugin_code(self, tool: Tool) -> str:
        """Extract source code from tool for verification"""
        try:
            # Get the source code of the tool's class or function
            if inspect.isclass(tool):
                source = inspect.getsource(tool)
            elif inspect.isfunction(tool):
                source = inspect.getsource(tool)
            else:
                # For instances, try to get the class source
                source = inspect.getsource(tool.__class__)
            
            return source
        except Exception as e:
            print(f"Warning: Could not extract source code for {tool.name}: {e}")
            return f"# Plugin: {tool.name}\n# Source extraction failed"
    
    def _extract_metadata(self, tool: Tool) -> PluginMetadata:
        """Extract metadata from tool"""
        return PluginMetadata(
            name=getattr(tool, 'name', 'unknown'),
            description=getattr(tool, 'description', 'No description provided'),
            author=getattr(tool, 'author', 'unknown'),
            version=getattr(tool, 'version', '1.0.0'),
            dependencies=getattr(tool, 'dependencies', []),
            tags=getattr(tool, 'tags', []),
            license=getattr(tool, 'license', 'MIT'),
            repository=getattr(tool, 'repository', None)
        )
    
    def load_plugins(self, plugins_dir: str, trust_verification: bool = None) -> Dict[str, bool]:
        """Load plugins with trust verification"""
        results = {}
        
        for filename in os.listdir(plugins_dir):
            if not filename.endswith(".py"):
                continue
            if filename in ["__init__.py", "plugin_manager.py", "secure_plugin_manager.py", "trust_manager.py"]:
                continue
            
            module_name = filename[:-3]
            module_path = f"{plugins_dir.replace('/', '.')}.{module_name}"
            
            try:
                # Dynamically import
                module = importlib.import_module(module_path)
                
                # Search for tools
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) or inspect.isfunction(obj):
                        if hasattr(obj, "name") and hasattr(obj, "description") and hasattr(obj, "run"):
                            # Instantiate if it's a class
                            if inspect.isclass(obj):
                                tool_instance = obj()
                            else:
                                tool_instance = obj
                            
                            if not getattr(tool_instance, "name", None):
                                continue
                            
                            # Register with trust verification
                            try:
                                success = self.register_tool(tool_instance, trust_verification=trust_verification)
                                results[tool_instance.name] = success
                            except (SecurityException, PluginVerificationException) as e:
                                print(f"❌ Failed to register {tool_instance.name}: {e}")
                                results[tool_instance.name] = False
                
            except Exception as e:
                print(f"❌ Failed to load module {module_name}: {e}")
                results[module_name] = False
        
        return results
    
    def get_tool_by_name(self, name: str) -> Optional[Tool]:
        """Get tool by name, checking trust status"""
        tool = TOOLS_REGISTRY.get(name)
        if tool is None:
            return None
        
        # Check if plugin is blocked
        if name in self.blocked_plugins:
            raise SecurityException(f"Plugin '{name}' is blocked due to low trust score")
        
        return tool
    
    def get_trust_info(self, tool_name: str) -> Optional[TrustScore]:
        """Get trust information for a tool"""
        return self.trust_scores.get(tool_name)
    
    def list_trusted_tools(self, min_score: float = None) -> List[str]:
        """List all tools with trust score above threshold"""
        if min_score is None:
            min_score = self.trust_threshold
        
        trusted_tools = []
        for tool_name, trust_score in self.trust_scores.items():
            if trust_score.zippy_trust_score >= min_score and tool_name not in self.blocked_plugins:
                trusted_tools.append(tool_name)
        
        return trusted_tools
    
    def list_blocked_tools(self) -> List[str]:
        """List all blocked tools"""
        return self.blocked_plugins.copy()
    
    def get_trust_summary(self) -> Dict[str, Any]:
        """Get summary of trust status"""
        total_plugins = len(TOOLS_REGISTRY)
        trusted_plugins = len(self.list_trusted_tools())
        blocked_plugins = len(self.blocked_plugins)
        
        avg_trust_score = 0.0
        if self.trust_scores:
            avg_trust_score = sum(score.zippy_trust_score for score in self.trust_scores.values()) / len(self.trust_scores)
        
        return {
            "total_plugins": total_plugins,
            "trusted_plugins": trusted_plugins,
            "blocked_plugins": blocked_plugins,
            "average_trust_score": avg_trust_score,
            "trust_threshold": self.trust_threshold,
            "trust_verification_enabled": self.trust_verification
        }
    
    def update_trust_threshold(self, new_threshold: float):
        """Update the trust threshold"""
        self.trust_threshold = new_threshold
        
        # Re-evaluate blocked plugins
        self.blocked_plugins = []
        for tool_name, trust_score in self.trust_scores.items():
            if trust_score.zippy_trust_score < self.trust_threshold:
                self.blocked_plugins.append(tool_name)
    
    def force_register_tool(self, tool: Tool, metadata: Optional[PluginMetadata] = None):
        """Force register a tool without trust verification (use with caution)"""
        print(f"⚠️  Force registering plugin '{tool.name}' without trust verification")
        return self.register_tool(tool, metadata, trust_verification=False)
    
    def unregister_tool(self, tool_name: str):
        """Unregister a tool"""
        if tool_name in TOOLS_REGISTRY:
            del TOOLS_REGISTRY[tool_name]
            print(f"🗑️  Unregistered plugin '{tool_name}'")
        
        if tool_name in self.trust_scores:
            del self.trust_scores[tool_name]
        
        if tool_name in self.plugin_metadata:
            del self.plugin_metadata[tool_name]
        
        if tool_name in self.blocked_plugins:
            self.blocked_plugins.remove(tool_name)
    
    def refresh_trust_scores(self):
        """Refresh trust scores for all registered plugins"""
        print("🔄 Refreshing trust scores...")
        
        for tool_name, tool in TOOLS_REGISTRY.items():
            try:
                plugin_code = self._extract_plugin_code(tool)
                metadata = self.plugin_metadata.get(tool_name, self._extract_metadata(tool))
                
                trust_score = asyncio.run(self.trust_manager.verify_plugin(plugin_code, metadata))
                self.trust_scores[tool_name] = trust_score
                
                # Update blocked status
                if trust_score.zippy_trust_score < self.trust_threshold:
                    if tool_name not in self.blocked_plugins:
                        self.blocked_plugins.append(tool_name)
                        print(f"🚫 Plugin '{tool_name}' blocked due to low trust score: {trust_score.zippy_trust_score:.2f}")
                else:
                    if tool_name in self.blocked_plugins:
                        self.blocked_plugins.remove(tool_name)
                        print(f"✅ Plugin '{tool_name}' unblocked with trust score: {trust_score.zippy_trust_score:.2f}")
                
            except Exception as e:
                print(f"❌ Failed to refresh trust score for '{tool_name}': {e}")
        
        print("✅ Trust score refresh completed")
