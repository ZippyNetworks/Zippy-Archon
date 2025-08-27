# plugins/marketplace.py

import json
import asyncio
import aiohttp
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import hashlib

from .trust_manager import PluginMetadata, TrustScore

@dataclass
class PluginListing:
    plugin_id: str
    name: str
    description: str
    author: str
    price_zippycoin: float
    trust_score: float
    download_count: int
    rating: float
    tags: List[str]
    version: str
    license: str
    repository: Optional[str]
    created_at: str
    updated_at: str
    status: str  # "active", "inactive", "flagged"

@dataclass
class PurchaseTransaction:
    transaction_id: str
    plugin_id: str
    buyer_wallet: str
    seller_wallet: str
    amount: float
    timestamp: str
    status: str  # "pending", "completed", "failed"
    description: str

class ZippyCoinClient:
    def __init__(self, api_url: str = "https://api.zippycoin.com"):
        self.api_url = api_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_balance(self, wallet_address: str) -> float:
        """Get ZippyCoin balance for a wallet"""
        try:
            async with self.session.get(f"{self.api_url}/balance/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("balance", 0.0)
                else:
                    print(f"Failed to get balance: {response.status}")
                    return 0.0
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0.0
    
    async def transfer(self, from_wallet: str, to_wallet: str, amount: float, description: str = "") -> Dict[str, Any]:
        """Transfer ZippyCoin between wallets"""
        try:
            payload = {
                "from_wallet": from_wallet,
                "to_wallet": to_wallet,
                "amount": amount,
                "description": description,
                "timestamp": datetime.now().isoformat()
            }
            
            async with self.session.post(f"{self.api_url}/transfer", json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"success": False, "error": f"Transfer failed: {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_wallet(self) -> Dict[str, Any]:
        """Create a new ZippyCoin wallet"""
        try:
            async with self.session.post(f"{self.api_url}/wallet/create") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"success": False, "error": f"Wallet creation failed: {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

class ZippyCoinMarketplace:
    def __init__(self, marketplace_url: str = "https://marketplace.zippycoin.com"):
        self.marketplace_url = marketplace_url
        self.listings: Dict[str, PluginListing] = {}
        self.transactions: List[PurchaseTransaction] = []
        self.cache_file = Path("marketplace_cache.json")
        self._load_cache()
    
    def _load_cache(self):
        """Load cached marketplace data"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    self.listings = {
                        plugin_id: PluginListing(**listing_data)
                        for plugin_id, listing_data in cache_data.get("listings", {}).items()
                    }
            except Exception as e:
                print(f"Warning: Could not load marketplace cache: {e}")
    
    def _save_cache(self):
        """Save marketplace data to cache"""
        try:
            cache_data = {
                "listings": {
                    plugin_id: asdict(listing)
                    for plugin_id, listing in self.listings.items()
                },
                "last_updated": datetime.now().isoformat()
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save marketplace cache: {e}")
    
    async def list_plugin(self, plugin: PluginListing, seller_wallet: str) -> bool:
        """List plugin for sale in marketplace"""
        try:
            # Verify plugin with ZippyTrust first
            from .trust_manager import ZippyTrustManager
            trust_manager = ZippyTrustManager()
            
            # Create metadata for verification
            metadata = PluginMetadata(
                name=plugin.name,
                description=plugin.description,
                author=plugin.author,
                version=plugin.version,
                dependencies=[],
                tags=plugin.tags,
                license=plugin.license,
                repository=plugin.repository
            )
            
            # For now, use a mock verification since we don't have the actual code
            # In a real implementation, you'd pass the actual plugin code
            mock_code = f"# Plugin: {plugin.name}\n# Author: {plugin.author}\n# Version: {plugin.version}"
            trust_score = await trust_manager.verify_plugin(mock_code, metadata)
            
            if trust_score.zippy_trust_score >= 0.8:  # High trust threshold for marketplace
                plugin.trust_score = trust_score.zippy_trust_score
                plugin.created_at = datetime.now().isoformat()
                plugin.updated_at = datetime.now().isoformat()
                plugin.status = "active"
                
                self.listings[plugin.plugin_id] = plugin
                self._save_cache()
                
                print(f"✅ Plugin '{plugin.name}' listed successfully with trust score: {trust_score.zippy_trust_score:.2f}")
                return True
            else:
                print(f"❌ Plugin '{plugin.name}' failed trust verification for marketplace listing")
                return False
                
        except Exception as e:
            print(f"❌ Failed to list plugin '{plugin.name}': {e}")
            return False
    
    async def purchase_plugin(self, plugin_id: str, buyer_wallet: str) -> Dict[str, Any]:
        """Purchase plugin using ZippyCoin"""
        listing = self.listings.get(plugin_id)
        if not listing:
            return {"success": False, "error": "Plugin not found"}
        
        if listing.status != "active":
            return {"success": False, "error": f"Plugin is not available (status: {listing.status})"}
        
        try:
            async with ZippyCoinClient() as coin_client:
                # Check buyer balance
                balance = await coin_client.get_balance(buyer_wallet)
                if balance < listing.price_zippycoin:
                    return {
                        "success": False, 
                        "error": f"Insufficient balance. Required: {listing.price_zippycoin}, Available: {balance}"
                    }
                
                # Process ZippyCoin transaction
                transaction_result = await coin_client.transfer(
                    from_wallet=buyer_wallet,
                    to_wallet=listing.author,  # Assuming author is the seller
                    amount=listing.price_zippycoin,
                    description=f"Plugin purchase: {listing.name}"
                )
                
                if transaction_result.get("success"):
                    # Create transaction record
                    transaction = PurchaseTransaction(
                        transaction_id=transaction_result.get("transaction_id", f"tx_{datetime.now().timestamp()}"),
                        plugin_id=plugin_id,
                        buyer_wallet=buyer_wallet,
                        seller_wallet=listing.author,
                        amount=listing.price_zippycoin,
                        timestamp=datetime.now().isoformat(),
                        status="completed",
                        description=f"Purchase of {listing.name}"
                    )
                    
                    self.transactions.append(transaction)
                    
                    # Update download count
                    listing.download_count += 1
                    listing.updated_at = datetime.now().isoformat()
                    self._save_cache()
                    
                    # Grant access to plugin (in a real implementation, this would download/install the plugin)
                    await self._grant_plugin_access(buyer_wallet, plugin_id)
                    
                    return {
                        "success": True,
                        "transaction": asdict(transaction),
                        "message": f"Successfully purchased {listing.name} for {listing.price_zippycoin} ZippyCoin"
                    }
                else:
                    return {
                        "success": False,
                        "error": transaction_result.get("error", "Transaction failed")
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _grant_plugin_access(self, buyer_wallet: str, plugin_id: str):
        """Grant access to purchased plugin"""
        # In a real implementation, this would:
        # 1. Download the plugin code
        # 2. Install it in the user's plugin directory
        # 3. Register it with the plugin manager
        # 4. Update user's plugin access permissions
        
        print(f"🎁 Granting access to plugin {plugin_id} for wallet {buyer_wallet}")
        
        # For now, just create a placeholder
        access_file = Path(f"plugin_access_{buyer_wallet}_{plugin_id}.json")
        access_data = {
            "wallet": buyer_wallet,
            "plugin_id": plugin_id,
            "purchased_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        with open(access_file, 'w') as f:
            json.dump(access_data, f, indent=2)
    
    def search_plugins(self, query: str = "", tags: List[str] = None, min_trust: float = 0.0, max_price: float = None) -> List[PluginListing]:
        """Search for plugins in the marketplace"""
        results = []
        
        for listing in self.listings.values():
            if listing.status != "active":
                continue
            
            # Filter by query
            if query and query.lower() not in listing.name.lower() and query.lower() not in listing.description.lower():
                continue
            
            # Filter by tags
            if tags and not any(tag in listing.tags for tag in tags):
                continue
            
            # Filter by trust score
            if listing.trust_score < min_trust:
                continue
            
            # Filter by price
            if max_price and listing.price_zippycoin > max_price:
                continue
            
            results.append(listing)
        
        # Sort by trust score (highest first)
        results.sort(key=lambda x: x.trust_score, reverse=True)
        
        return results
    
    def get_plugin_details(self, plugin_id: str) -> Optional[PluginListing]:
        """Get detailed information about a plugin"""
        return self.listings.get(plugin_id)
    
    def get_user_purchases(self, wallet_address: str) -> List[PurchaseTransaction]:
        """Get purchase history for a wallet"""
        return [
            tx for tx in self.transactions
            if tx.buyer_wallet == wallet_address and tx.status == "completed"
        ]
    
    def get_author_plugins(self, author_wallet: str) -> List[PluginListing]:
        """Get all plugins by an author"""
        return [
            listing for listing in self.listings.values()
            if listing.author == author_wallet
        ]
    
    async def update_plugin_listing(self, plugin_id: str, updates: Dict[str, Any]) -> bool:
        """Update a plugin listing"""
        if plugin_id not in self.listings:
            return False
        
        listing = self.listings[plugin_id]
        
        # Update allowed fields
        allowed_fields = ["price_zippycoin", "description", "tags", "version"]
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(listing, field, value)
        
        listing.updated_at = datetime.now().isoformat()
        self._save_cache()
        
        return True
    
    def remove_plugin_listing(self, plugin_id: str, author_wallet: str) -> bool:
        """Remove a plugin listing (only by author)"""
        listing = self.listings.get(plugin_id)
        if not listing or listing.author != author_wallet:
            return False
        
        listing.status = "inactive"
        listing.updated_at = datetime.now().isoformat()
        self._save_cache()
        
        return True
    
    def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        total_listings = len(self.listings)
        active_listings = len([l for l in self.listings.values() if l.status == "active"])
        total_downloads = sum(l.download_count for l in self.listings.values())
        total_volume = sum(tx.amount for tx in self.transactions if tx.status == "completed")
        
        return {
            "total_listings": total_listings,
            "active_listings": active_listings,
            "total_downloads": total_downloads,
            "total_volume_zippycoin": total_volume,
            "average_trust_score": sum(l.trust_score for l in self.listings.values()) / max(len(self.listings), 1),
            "last_updated": datetime.now().isoformat()
        }
