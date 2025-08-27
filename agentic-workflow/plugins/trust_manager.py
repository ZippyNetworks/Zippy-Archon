# plugins/trust_manager.py

import hashlib
import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import aiohttp
from pathlib import Path

@dataclass
class TrustScore:
    plugin_id: str
    zippy_trust_score: float  # 0.0 - 1.0
    verification_status: str  # "verified", "pending", "flagged", "unknown"
    audit_trail: List[Dict[str, Any]]
    reputation_score: float
    usage_count: int
    last_updated: str
    author: str
    version: str
    security_checks: Dict[str, bool]
    code_quality_score: float

@dataclass
class PluginMetadata:
    name: str
    description: str
    author: str
    version: str
    dependencies: List[str]
    tags: List[str]
    license: str
    repository: Optional[str] = None

class ZippyTrustManager:
    def __init__(self, trust_registry_url: Optional[str] = None):
        self.trust_registry_url = trust_registry_url or "https://api.zippytrust.com"
        self.trust_scores: Dict[str, TrustScore] = {}
        self.verification_rules = self._load_verification_rules()
        self.cache_file = Path("trust_cache.json")
        self._load_cache()
    
    def _load_verification_rules(self) -> Dict[str, Any]:
        """Load verification rules for plugin trust scoring"""
        return {
            "code_quality": {
                "min_complexity": 0.1,
                "max_complexity": 0.8,
                "require_docstrings": True,
                "require_type_hints": True
            },
            "security": {
                "check_exec": True,
                "check_network": True,
                "check_file_access": True,
                "check_imports": True
            },
            "reputation": {
                "min_usage_count": 5,
                "min_rating": 3.0,
                "max_flagged_reports": 2
            }
        }
    
    def _load_cache(self):
        """Load cached trust scores from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    for plugin_id, score_data in cache_data.items():
                        self.trust_scores[plugin_id] = TrustScore(**score_data)
            except Exception as e:
                print(f"Warning: Could not load trust cache: {e}")
    
    def _save_cache(self):
        """Save trust scores to disk cache"""
        try:
            cache_data = {
                plugin_id: asdict(score) 
                for plugin_id, score in self.trust_scores.items()
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save trust cache: {e}")
    
    async def verify_plugin(self, plugin_code: str, metadata: PluginMetadata) -> TrustScore:
        """Verify plugin using ZippyTrust ecosystem"""
        plugin_hash = hashlib.sha256(plugin_code.encode()).hexdigest()
        
        # Check cache first
        if plugin_hash in self.trust_scores:
            cached_score = self.trust_scores[plugin_hash]
            # Check if cache is still valid (less than 24 hours old)
            last_updated = datetime.fromisoformat(cached_score.last_updated)
            if (datetime.now() - last_updated).days < 1:
                return cached_score
        
        # Check against ZippyTrust registry
        trust_data = await self._query_zippytrust_registry(plugin_hash, metadata)
        
        # Calculate trust score based on multiple factors
        score = await self._calculate_trust_score(plugin_code, metadata, trust_data)
        
        # Store in cache
        self.trust_scores[plugin_hash] = score
        self._save_cache()
        
        return score
    
    async def _query_zippytrust_registry(self, plugin_hash: str, metadata: PluginMetadata) -> Dict[str, Any]:
        """Query ZippyTrust blockchain/registry for plugin verification"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "plugin_hash": plugin_hash,
                    "metadata": asdict(metadata),
                    "timestamp": datetime.now().isoformat()
                }
                
                async with session.post(
                    f"{self.trust_registry_url}/verify",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Warning: ZippyTrust registry returned {response.status}")
                        return self._get_default_trust_data()
        except Exception as e:
            print(f"Warning: Could not query ZippyTrust registry: {e}")
            return self._get_default_trust_data()
    
    def _get_default_trust_data(self) -> Dict[str, Any]:
        """Return default trust data when registry is unavailable"""
        return {
            "audit_trail": [],
            "reputation": 0.5,
            "usage_count": 0,
            "last_updated": datetime.now().isoformat(),
            "security_checks": {
                "code_analysis": False,
                "dependency_check": False,
                "malware_scan": False
            }
        }
    
    async def _calculate_trust_score(self, plugin_code: str, metadata: PluginMetadata, trust_data: Dict[str, Any]) -> TrustScore:
        """Calculate comprehensive trust score"""
        scores = []
        
        # Code quality analysis (30% weight)
        code_quality = self._analyze_code_quality(plugin_code)
        scores.append(("code_quality", code_quality, 0.3))
        
        # Security analysis (40% weight)
        security_score = self._analyze_security(plugin_code)
        scores.append(("security", security_score, 0.4))
        
        # Reputation score (20% weight)
        reputation = trust_data.get("reputation", 0.5)
        scores.append(("reputation", reputation, 0.2))
        
        # Author reputation (10% weight)
        author_score = await self._get_author_reputation(metadata.author)
        scores.append(("author", author_score, 0.1))
        
        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in scores)
        
        # Determine verification status
        verification_status = self._determine_status(total_score, trust_data)
        
        return TrustScore(
            plugin_id=metadata.name,
            zippy_trust_score=total_score,
            verification_status=verification_status,
            audit_trail=trust_data.get("audit_trail", []),
            reputation_score=reputation,
            usage_count=trust_data.get("usage_count", 0),
            last_updated=datetime.now().isoformat(),
            author=metadata.author,
            version=metadata.version,
            security_checks=trust_data.get("security_checks", {}),
            code_quality_score=code_quality
        )
    
    def _analyze_code_quality(self, code: str) -> float:
        """Analyze code quality metrics"""
        score = 0.0
        lines = code.split('\n')
        
        # Check for docstrings
        if '"""' in code or "'''" in code:
            score += 0.2
        
        # Check for type hints
        if ':' in code and '->' in code:
            score += 0.2
        
        # Check for proper imports
        if 'import ' in code or 'from ' in code:
            score += 0.1
        
        # Check for error handling
        if 'try:' in code and 'except:' in code:
            score += 0.2
        
        # Check for logging
        if 'logging' in code or 'print(' in code:
            score += 0.1
        
        # Check for reasonable complexity
        if len(lines) > 10 and len(lines) < 500:
            score += 0.2
        
        return min(score, 1.0)
    
    def _analyze_security(self, code: str) -> float:
        """Analyze security aspects of the code"""
        score = 1.0
        security_issues = []
        
        # Check for dangerous functions
        dangerous_functions = [
            'eval(', 'exec(', 'os.system(', 'subprocess.call(',
            'pickle.loads(', 'marshal.loads(', 'yaml.load('
        ]
        
        for func in dangerous_functions:
            if func in code:
                security_issues.append(f"Dangerous function: {func}")
                score -= 0.3
        
        # Check for hardcoded secrets
        if any(pattern in code.lower() for pattern in ['password', 'secret', 'key', 'token']):
            if any(pattern in code for pattern in ['= "', "= '", '= """']):
                security_issues.append("Potential hardcoded secrets")
                score -= 0.2
        
        # Check for network access
        if any(pattern in code for pattern in ['requests.', 'urllib.', 'http.']):
            # Network access is not inherently bad, but needs review
            score -= 0.1
        
        return max(score, 0.0)
    
    async def _get_author_reputation(self, author: str) -> float:
        """Get author reputation from ZippyTrust"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.trust_registry_url}/author/{author}",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("reputation", 0.5)
                    else:
                        return 0.5
        except Exception:
            return 0.5
    
    def _determine_status(self, score: float, trust_data: Dict[str, Any]) -> str:
        """Determine verification status based on score and trust data"""
        if score >= 0.9:
            return "verified"
        elif score >= 0.7:
            return "pending"
        elif score >= 0.5:
            return "flagged"
        else:
            return "unknown"
    
    def get_trust_info(self, plugin_id: str) -> Optional[TrustScore]:
        """Get trust information for a plugin"""
        return self.trust_scores.get(plugin_id)
    
    def list_trusted_plugins(self, min_score: float = 0.7) -> List[TrustScore]:
        """List all plugins with trust score above threshold"""
        return [
            score for score in self.trust_scores.values()
            if score.zippy_trust_score >= min_score
        ]
    
    def update_trust_score(self, plugin_id: str, new_score: float, reason: str):
        """Update trust score (for manual adjustments)"""
        if plugin_id in self.trust_scores:
            self.trust_scores[plugin_id].zippy_trust_score = new_score
            self.trust_scores[plugin_id].last_updated = datetime.now().isoformat()
            self.trust_scores[plugin_id].audit_trail.append({
                "timestamp": datetime.now().isoformat(),
                "action": "manual_update",
                "reason": reason,
                "new_score": new_score
            })
            self._save_cache()
