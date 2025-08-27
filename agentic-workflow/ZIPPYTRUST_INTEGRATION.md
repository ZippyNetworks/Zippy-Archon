# 🛡️ ZippyTrust & 🪙 ZippyCoin Integration

This document describes the integration of ZippyTrust security verification and ZippyCoin marketplace functionality into the Zippy Archon agentic workflow system.

## Overview

The ZippyTrust and ZippyCoin integration provides:

- **🛡️ Trust Verification**: Automated security and code quality analysis for plugins
- **🪙 Marketplace**: Buy and sell plugins using ZippyCoin cryptocurrency
- **🔒 Secure Plugin Management**: Trust-based plugin loading and execution
- **📊 Analytics**: Comprehensive trust and marketplace analytics

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ZippyTrust    │    │  ZippyCoin      │    │   Marketplace   │
│   Manager       │    │   Client        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────┐
         │           Secure Plugin Manager                 │
         │  • Trust verification                          │
         │  • Plugin loading with security checks        │
         │  • Marketplace integration                     │
         └─────────────────────────────────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────┐
         │           Streamlit UI                          │
         │  • Trust dashboard                             │
         │  • Marketplace interface                       │
         │  • Analytics and reporting                     │
         └─────────────────────────────────────────────────┘
```

## Components

### 1. ZippyTrust Manager (`plugins/trust_manager.py`)

The core trust verification system that analyzes plugins for:

- **Code Quality**: Documentation, type hints, error handling
- **Security**: Dangerous functions, hardcoded secrets, network access
- **Reputation**: Author history, usage statistics
- **Audit Trail**: Complete verification history

#### Key Features:

```python
# Initialize trust manager
trust_manager = ZippyTrustManager()

# Verify a plugin
trust_score = await trust_manager.verify_plugin(plugin_code, metadata)

# Get trust information
trust_info = trust_manager.get_trust_info("plugin_name")

# List trusted plugins
trusted_plugins = trust_manager.list_trusted_plugins(min_score=0.7)
```

#### Trust Score Calculation:

- **Code Quality (30%)**: Documentation, type hints, error handling
- **Security (40%)**: Dangerous functions, secrets, network access
- **Reputation (20%)**: Author history, community feedback
- **Author Reputation (10%)**: Individual author trust score

### 2. Secure Plugin Manager (`plugins/secure_plugin_manager.py`)

Enhanced plugin manager with trust verification:

```python
# Initialize with trust verification
secure_manager = SecurePluginManager(trust_threshold=0.7)

# Register plugin with trust verification
success = secure_manager.register_tool(plugin, trust_verification=True)

# Get trusted tools only
trusted_tools = secure_manager.list_trusted_tools()

# Check if plugin is blocked
if tool_name in secure_manager.blocked_plugins:
    print("Plugin blocked due to low trust score")
```

#### Security Features:

- **Automatic Verification**: All plugins verified before loading
- **Trust Thresholds**: Configurable minimum trust scores
- **Blocked Plugins**: Automatic blocking of low-trust plugins
- **Audit Trail**: Complete verification history

### 3. ZippyCoin Marketplace (`plugins/marketplace.py`)

Cryptocurrency-based plugin marketplace:

```python
# Initialize marketplace
marketplace = ZippyCoinMarketplace()

# List a plugin for sale
listing = PluginListing(
    plugin_id="my_plugin",
    name="My Plugin",
    price_zippycoin=10.0,
    # ... other metadata
)
success = await marketplace.list_plugin(listing, seller_wallet)

# Purchase a plugin
result = await marketplace.purchase_plugin("plugin_id", buyer_wallet)
```

#### Marketplace Features:

- **Plugin Listings**: Secure plugin marketplace
- **ZippyCoin Payments**: Cryptocurrency-based transactions
- **Trust Integration**: Only high-trust plugins can be listed
- **Purchase History**: Complete transaction records

### 4. ZippyCoin Client (`plugins/marketplace.py`)

Blockchain client for ZippyCoin transactions:

```python
async with ZippyCoinClient() as client:
    # Get wallet balance
    balance = await client.get_balance(wallet_address)
    
    # Transfer ZippyCoin
    result = await client.transfer(from_wallet, to_wallet, amount)
    
    # Create new wallet
    wallet = await client.create_wallet()
```

## Usage Examples

### Basic Trust Verification

```python
from plugins.trust_manager import ZippyTrustManager, PluginMetadata
from plugins.secure_plugin_manager import SecurePluginManager

# Initialize managers
trust_manager = ZippyTrustManager()
secure_manager = SecurePluginManager(trust_threshold=0.7)

# Create plugin metadata
metadata = PluginMetadata(
    name="my_plugin",
    description="A useful plugin",
    author="trusted_author",
    version="1.0.0",
    dependencies=[],
    tags=["utility"],
    license="MIT"
)

# Verify plugin
plugin_code = """
def my_plugin(data):
    return {"result": "processed"}
"""

trust_score = await trust_manager.verify_plugin(plugin_code, metadata)
print(f"Trust score: {trust_score.zippy_trust_score:.2f}")
```

### Marketplace Integration

```python
from plugins.marketplace import ZippyCoinMarketplace, PluginListing

# Initialize marketplace
marketplace = ZippyCoinMarketplace()

# List a plugin for sale
listing = PluginListing(
    plugin_id="my_plugin",
    name="My Plugin",
    description="A useful plugin",
    author="my_wallet_address",
    price_zippycoin=15.0,
    trust_score=0.9,
    download_count=0,
    rating=0.0,
    tags=["utility", "demo"],
    version="1.0.0",
    license="MIT"
)

# List the plugin
success = await marketplace.list_plugin(listing, "my_wallet_address")

# Search for plugins
plugins = marketplace.search_plugins(
    query="utility",
    min_trust=0.8,
    max_price=20.0
)

# Purchase a plugin
if plugins:
    result = await marketplace.purchase_plugin(
        plugins[0].plugin_id, 
        "buyer_wallet_address"
    )
```

### Streamlit UI

Run the integrated UI:

```bash
cd agentic-workflow
streamlit run trust_marketplace_ui.py
```

The UI provides:

- **Trust Dashboard**: Plugin trust scores and verification status
- **Marketplace**: Browse and purchase plugins
- **My Plugins**: Manage purchased and authored plugins
- **Analytics**: Trust and marketplace statistics

## Configuration

### Environment Variables

```bash
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

### Trust Thresholds

| Threshold | Description | Use Case |
|-----------|-------------|----------|
| 0.9+ | High Trust | Production systems, critical applications |
| 0.7-0.9 | Medium Trust | Development, testing, trusted authors |
| 0.5-0.7 | Low Trust | Experimental, personal use |
| <0.5 | Untrusted | Blocked by default |

## Security Features

### Code Analysis

The trust system analyzes plugins for:

- **Dangerous Functions**: `eval()`, `exec()`, `os.system()`, etc.
- **Hardcoded Secrets**: API keys, passwords, tokens
- **Network Access**: Unauthorized network requests
- **File Access**: Unsafe file operations

### Verification Process

1. **Code Extraction**: Extract source code from plugin
2. **Static Analysis**: Analyze code for security issues
3. **Metadata Verification**: Check author, version, dependencies
4. **Reputation Check**: Query ZippyTrust for author history
5. **Score Calculation**: Compute weighted trust score
6. **Status Assignment**: Assign verification status

### Audit Trail

Every verification creates an audit trail:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "plugin_id": "my_plugin",
  "trust_score": 0.85,
  "verification_status": "verified",
  "security_checks": {
    "code_analysis": true,
    "dependency_check": true,
    "malware_scan": true
  },
  "audit_trail": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "action": "verification",
      "details": "Plugin verified successfully"
    }
  ]
}
```

## Demo Plugins

The system includes demo plugins to showcase trust features:

### Trusted Plugin (`plugins/demo_trusted_plugin.py`)

A high-quality plugin that demonstrates best practices:

- ✅ Proper documentation
- ✅ Type hints
- ✅ Error handling
- ✅ Security checks
- ✅ Audit trail
- ✅ No dangerous functions

### Unsafe Plugin Examples

Demonstrates what would fail trust verification:

- ❌ Uses `os.system()` (dangerous)
- ❌ Hardcoded secrets
- ❌ No error handling
- ❌ Poor documentation

## API Reference

### ZippyTrustManager

```python
class ZippyTrustManager:
    async def verify_plugin(self, plugin_code: str, metadata: PluginMetadata) -> TrustScore
    def get_trust_info(self, plugin_id: str) -> Optional[TrustScore]
    def list_trusted_plugins(self, min_score: float = 0.7) -> List[TrustScore]
    def update_trust_score(self, plugin_id: str, new_score: float, reason: str)
```

### SecurePluginManager

```python
class SecurePluginManager:
    def register_tool(self, tool: Tool, metadata: Optional[PluginMetadata] = None) -> bool
    def get_tool_by_name(self, name: str) -> Optional[Tool]
    def list_trusted_tools(self, min_score: float = None) -> List[str]
    def get_trust_summary(self) -> Dict[str, Any]
    def refresh_trust_scores(self)
```

### ZippyCoinMarketplace

```python
class ZippyCoinMarketplace:
    async def list_plugin(self, plugin: PluginListing, seller_wallet: str) -> bool
    async def purchase_plugin(self, plugin_id: str, buyer_wallet: str) -> Dict[str, Any]
    def search_plugins(self, query: str = "", tags: List[str] = None, min_trust: float = 0.0) -> List[PluginListing]
    def get_marketplace_stats(self) -> Dict[str, Any]
```

## Troubleshooting

### Common Issues

1. **Plugin Verification Fails**
   - Check code quality (documentation, type hints)
   - Remove dangerous functions
   - Add proper error handling

2. **Marketplace Connection Issues**
   - Verify API endpoints
   - Check network connectivity
   - Ensure wallet addresses are valid

3. **Trust Score Too Low**
   - Improve code documentation
   - Add type hints
   - Implement proper error handling
   - Remove security issues

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Initialize managers with debug
trust_manager = ZippyTrustManager()
secure_manager = SecurePluginManager(trust_threshold=0.7)
```

## Future Enhancements

- **Blockchain Integration**: Full blockchain-based trust verification
- **AI-Powered Analysis**: Machine learning for code quality assessment
- **Community Reviews**: User reviews and ratings
- **Automated Auditing**: Continuous security monitoring
- **Plugin Versioning**: Version control and update management
- **Multi-Currency Support**: Support for other cryptocurrencies

## Contributing

To contribute to the ZippyTrust and ZippyCoin integration:

1. Follow the trust guidelines in your plugins
2. Add comprehensive documentation
3. Include proper error handling
4. Avoid dangerous functions
5. Test thoroughly before submission

## License

This integration is part of the Zippy Archon project and follows the same licensing terms.
