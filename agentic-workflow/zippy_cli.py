#!/usr/bin/env python3
"""
ZippyTrust & ZippyCoin CLI

A comprehensive command-line interface for managing the ZippyTrust and ZippyCoin ecosystem.
"""

import click
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from plugins.trust_manager import ZippyTrustManager, PluginMetadata
from plugins.secure_plugin_manager import SecurePluginManager
from plugins.marketplace import ZippyCoinMarketplace, ZippyCoinClient
from vscode_integration import VSCodeIntegration, MultiAgentOrchestrator

# Configure Click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.0.0', prog_name='ZippyTrust CLI')
def cli():
    """
    🛡️ ZippyTrust & 🪙 ZippyCoin Command Line Interface
    
    Manage your plugin ecosystem with trust verification and marketplace integration.
    """
    pass

# Trust Management Commands
@cli.group()
def trust():
    """Manage plugin trust verification and security."""
    pass

@trust.command()
@click.argument('plugin_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for detailed results')
def verify(plugin_path: str, output: Optional[str]):
    """Verify a plugin's trust score and security."""
    click.echo(f"🔍 Verifying plugin: {plugin_path}")
    
    async def verify_plugin():
        try:
            # Initialize managers
            trust_manager = ZippyTrustManager()
            
            # Read plugin code
            plugin_file = Path(plugin_path)
            plugin_code = plugin_file.read_text()
            
            # Extract metadata
            metadata = extract_plugin_metadata(plugin_code, plugin_file.name)
            
            # Verify plugin
            trust_score = await trust_manager.verify_plugin(plugin_code, metadata)
            
            # Display results
            click.echo(f"\n📊 Trust Verification Results:")
            click.echo(f"   Plugin: {metadata.name}")
            click.echo(f"   Author: {metadata.author}")
            click.echo(f"   Version: {metadata.version}")
            click.echo(f"   Trust Score: {trust_score.zippy_trust_score:.2f}")
            click.echo(f"   Status: {trust_score.verification_status}")
            click.echo(f"   Code Quality: {trust_score.code_quality_score:.2f}")
            
            # Security checks
            click.echo(f"\n🔒 Security Checks:")
            for check, passed in trust_score.security_checks.items():
                status = "✅" if passed else "❌"
                click.echo(f"   {status} {check}")
            
            # Save detailed results if requested
            if output:
                results = {
                    "plugin_path": plugin_path,
                    "metadata": {
                        "name": metadata.name,
                        "description": metadata.description,
                        "author": metadata.author,
                        "version": metadata.version,
                        "dependencies": metadata.dependencies,
                        "tags": metadata.tags,
                        "license": metadata.license
                    },
                    "trust_score": trust_score.zippy_trust_score,
                    "verification_status": trust_score.verification_status,
                    "code_quality_score": trust_score.code_quality_score,
                    "security_checks": trust_score.security_checks,
                    "audit_trail": trust_score.audit_trail,
                    "verified_at": datetime.now().isoformat()
                }
                
                with open(output, 'w') as f:
                    json.dump(results, f, indent=2)
                click.echo(f"\n💾 Detailed results saved to: {output}")
            
            # Recommendations
            if trust_score.zippy_trust_score < 0.7:
                click.echo(f"\n⚠️  Recommendations to improve trust score:")
                if trust_score.code_quality_score < 0.8:
                    click.echo("   • Add comprehensive documentation")
                    click.echo("   • Include type hints")
                    click.echo("   • Add error handling")
                if any(not check for check in trust_score.security_checks.values()):
                    click.echo("   • Review security practices")
                    click.echo("   • Remove dangerous functions")
                    click.echo("   • Secure sensitive data")
            
        except Exception as e:
            click.echo(f"❌ Verification failed: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(verify_plugin())

@trust.command()
@click.option('--min-score', '-m', type=float, default=0.7, help='Minimum trust score threshold')
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'csv']), default='table', help='Output format')
def list(min_score: float, format: str):
    """List all trusted plugins."""
    click.echo(f"📋 Listing plugins with trust score >= {min_score}")
    
    async def list_plugins():
        try:
            trust_manager = ZippyTrustManager()
            trusted_plugins = trust_manager.list_trusted_plugins(min_score=min_score)
            
            if not trusted_plugins:
                click.echo("No plugins found matching criteria.")
                return
            
            if format == 'table':
                click.echo(f"\n{'Plugin':<20} {'Author':<15} {'Score':<8} {'Status':<10}")
                click.echo("-" * 60)
                for plugin in trusted_plugins:
                    click.echo(f"{plugin.plugin_id:<20} {plugin.author:<15} {plugin.zippy_trust_score:<8.2f} {plugin.verification_status:<10}")
            
            elif format == 'json':
                results = []
                for plugin in trusted_plugins:
                    results.append({
                        "plugin_id": plugin.plugin_id,
                        "author": plugin.author,
                        "trust_score": plugin.zippy_trust_score,
                        "status": plugin.verification_status,
                        "version": plugin.version,
                        "last_updated": plugin.last_updated
                    })
                click.echo(json.dumps(results, indent=2))
            
            elif format == 'csv':
                click.echo("plugin_id,author,trust_score,status,version,last_updated")
                for plugin in trusted_plugins:
                    click.echo(f"{plugin.plugin_id},{plugin.author},{plugin.zippy_trust_score},{plugin.verification_status},{plugin.version},{plugin.last_updated}")
            
        except Exception as e:
            click.echo(f"❌ Failed to list plugins: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(list_plugins())

@trust.command()
@click.argument('plugin_id')
@click.argument('new_score', type=float)
@click.argument('reason')
def update(plugin_id: str, new_score: float, reason: str):
    """Update a plugin's trust score manually."""
    click.echo(f"🔄 Updating trust score for {plugin_id} to {new_score}")
    
    try:
        trust_manager = ZippyTrustManager()
        trust_manager.update_trust_score(plugin_id, new_score, reason)
        click.echo(f"✅ Trust score updated successfully")
    except Exception as e:
        click.echo(f"❌ Failed to update trust score: {e}", err=True)
        sys.exit(1)

# Marketplace Commands
@cli.group()
def marketplace():
    """Manage plugin marketplace and ZippyCoin transactions."""
    pass

@marketplace.command()
@click.option('--query', '-q', help='Search query')
@click.option('--min-trust', '-t', type=float, default=0.0, help='Minimum trust score')
@click.option('--max-price', '-p', type=float, help='Maximum price in ZippyCoin')
@click.option('--tags', help='Comma-separated tags to filter by')
def search(query: Optional[str], min_trust: float, max_price: Optional[float], tags: Optional[str]):
    """Search for plugins in the marketplace."""
    click.echo("🔍 Searching marketplace...")
    
    async def search_marketplace():
        try:
            marketplace = ZippyCoinMarketplace()
            
            tag_list = tags.split(',') if tags else None
            plugins = marketplace.search_plugins(
                query=query or "",
                tags=tag_list,
                min_trust=min_trust,
                max_price=max_price
            )
            
            if not plugins:
                click.echo("No plugins found matching criteria.")
                return
            
            click.echo(f"\n📦 Found {len(plugins)} plugins:")
            click.echo(f"{'Name':<20} {'Author':<15} {'Price':<10} {'Trust':<8} {'Downloads':<10}")
            click.echo("-" * 70)
            
            for plugin in plugins:
                click.echo(f"{plugin.name:<20} {plugin.author:<15} {plugin.price_zippycoin:<10.2f} {plugin.trust_score:<8.2f} {plugin.download_count:<10}")
            
        except Exception as e:
            click.echo(f"❌ Search failed: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(search_marketplace())

@marketplace.command()
@click.argument('plugin_id')
@click.argument('wallet_address')
def purchase(plugin_id: str, wallet_address: str):
    """Purchase a plugin using ZippyCoin."""
    click.echo(f"🛒 Purchasing plugin: {plugin_id}")
    
    async def purchase_plugin():
        try:
            marketplace = ZippyCoinMarketplace()
            result = await marketplace.purchase_plugin(plugin_id, wallet_address)
            
            if result["success"]:
                click.echo(f"✅ Purchase successful!")
                click.echo(f"   Transaction ID: {result['transaction']['transaction_id']}")
                click.echo(f"   Amount: {result['transaction']['amount']} ZC")
                click.echo(f"   Message: {result['message']}")
            else:
                click.echo(f"❌ Purchase failed: {result['error']}")
                sys.exit(1)
            
        except Exception as e:
            click.echo(f"❌ Purchase failed: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(purchase_plugin())

@marketplace.command()
@click.argument('wallet_address')
def balance(wallet_address: str):
    """Check ZippyCoin wallet balance."""
    click.echo(f"💰 Checking balance for wallet: {wallet_address}")
    
    async def check_balance():
        try:
            async with ZippyCoinClient() as client:
                balance = await client.get_balance(wallet_address)
                click.echo(f"Balance: {balance:.2f} ZC")
        except Exception as e:
            click.echo(f"❌ Failed to check balance: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(check_balance())

@marketplace.command()
@click.argument('wallet_address')
def history(wallet_address: str):
    """View purchase history for a wallet."""
    click.echo(f"📜 Purchase history for wallet: {wallet_address}")
    
    async def view_history():
        try:
            marketplace = ZippyCoinMarketplace()
            purchases = marketplace.get_user_purchases(wallet_address)
            
            if not purchases:
                click.echo("No purchase history found.")
                return
            
            click.echo(f"\n{'Plugin':<20} {'Amount':<10} {'Date':<20} {'Status':<10}")
            click.echo("-" * 65)
            
            for purchase in purchases:
                date = datetime.fromisoformat(purchase.timestamp).strftime("%Y-%m-%d %H:%M")
                click.echo(f"{purchase.plugin_id:<20} {purchase.amount:<10.2f} {date:<20} {purchase.status:<10}")
            
        except Exception as e:
            click.echo(f"❌ Failed to get history: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(view_history())

# Plugin Management Commands
@cli.group()
def plugin():
    """Manage local plugins and development."""
    pass

@plugin.command()
@click.argument('name')
@click.option('--description', '-d', help='Plugin description')
@click.option('--author', '-a', help='Plugin author')
@click.option('--tags', '-t', help='Comma-separated tags')
@click.option('--output', '-o', type=click.Path(), help='Output directory')
def create(name: str, description: str, author: str, tags: str, output: Optional[str]):
    """Create a new plugin with ZippyTrust best practices."""
    click.echo(f"🛠️  Creating new plugin: {name}")
    
    async def create_plugin():
        try:
            integration = VSCodeIntegration()
            
            # Parse tags
            tag_list = tags.split(',') if tags else []
            
            # Generate plugin template
            plugin_code = integration.generate_plugin_template(
                name=name,
                description=description or f"A {name} plugin",
                author=author or "unknown",
                tags=tag_list
            )
            
            # Determine output path
            if output:
                output_dir = Path(output)
            else:
                output_dir = Path.cwd() / "plugins"
            
            output_dir.mkdir(exist_ok=True)
            plugin_file = output_dir / f"{name}.py"
            
            # Save plugin
            plugin_file.write_text(plugin_code)
            
            click.echo(f"✅ Plugin created successfully!")
            click.echo(f"   File: {plugin_file}")
            click.echo(f"   Name: {name}")
            click.echo(f"   Author: {author or 'unknown'}")
            click.echo(f"   Tags: {', '.join(tag_list) if tag_list else 'none'}")
            
            # Verify the new plugin
            click.echo(f"\n🔍 Verifying new plugin...")
            metadata = integration.extract_plugin_metadata(plugin_code, f"{name}.py")
            trust_score = await integration.trust_manager.verify_plugin(plugin_code, metadata)
            
            click.echo(f"   Trust Score: {trust_score.zippy_trust_score:.2f}")
            click.echo(f"   Status: {trust_score.verification_status}")
            
        except Exception as e:
            click.echo(f"❌ Failed to create plugin: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(create_plugin())

@plugin.command()
@click.argument('plugin_path', type=click.Path(exists=True))
@click.option('--test-data', '-d', help='JSON test data')
def test(plugin_path: str, test_data: Optional[str]):
    """Test a plugin with sample data."""
    click.echo(f"🧪 Testing plugin: {plugin_path}")
    
    async def test_plugin():
        try:
            integration = VSCodeIntegration()
            
            # Parse test data
            if test_data:
                try:
                    data = json.loads(test_data)
                except json.JSONDecodeError:
                    click.echo("❌ Invalid JSON test data", err=True)
                    sys.exit(1)
            else:
                data = {"test": "data", "numbers": [1, 2, 3, 4, 5]}
            
            # Test plugin
            result = await integration.test_plugin(plugin_path, data)
            
            if result["success"]:
                click.echo(f"✅ Test passed!")
                click.echo(f"   Execution time: {result['execution_time']:.3f}s")
                click.echo(f"   Result: {json.dumps(result['result'], indent=2)}")
            else:
                click.echo(f"❌ Test failed: {result['error']}")
                sys.exit(1)
            
        except Exception as e:
            click.echo(f"❌ Test failed: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(test_plugin())

@plugin.command()
@click.argument('plugin_path', type=click.Path(exists=True))
@click.argument('price', type=float)
@click.argument('wallet_address')
def deploy(plugin_path: str, price: float, wallet_address: str):
    """Deploy a plugin to the marketplace."""
    click.echo(f"🚀 Deploying plugin to marketplace...")
    
    async def deploy_plugin():
        try:
            integration = VSCodeIntegration()
            
            # Create marketplace listing
            listing = await integration.create_marketplace_listing(
                plugin_path, price, wallet_address
            )
            
            # Deploy to marketplace
            success = await integration.marketplace.list_plugin(listing, wallet_address)
            
            if success:
                click.echo(f"✅ Plugin deployed successfully!")
                click.echo(f"   Plugin ID: {listing.plugin_id}")
                click.echo(f"   Price: {listing.price_zippycoin} ZC")
                click.echo(f"   Trust Score: {listing.trust_score:.2f}")
            else:
                click.echo(f"❌ Deployment failed")
                sys.exit(1)
            
        except Exception as e:
            click.echo(f"❌ Deployment failed: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(deploy_plugin())

# VS Code Integration Commands
@cli.group()
def vscode():
    """Manage VS Code integration and development workflow."""
    pass

@vscode.command()
@click.option('--host', default='localhost', help='Host to bind to')
@click.option('--port', default=8765, type=int, help='Port to bind to')
def server(host: str, port: int):
    """Start the VS Code integration server."""
    click.echo(f"🚀 Starting VS Code Integration Server...")
    click.echo(f"📡 WebSocket server: ws://{host}:{port}")
    click.echo(f"🔌 Connect your VS Code extension to start developing!")
    
    async def start_server():
        try:
            integration = VSCodeIntegration()
            await integration.start_server(host=host, port=port)
        except KeyboardInterrupt:
            click.echo("\n👋 Server stopped by user")
        except Exception as e:
            click.echo(f"❌ Server failed: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(start_server())

@vscode.command()
@click.argument('workflow_id')
@click.argument('workflow_file', type=click.Path(exists=True))
def workflow(workflow_id: str, workflow_file: str):
    """Execute a multi-agent workflow."""
    click.echo(f"🔄 Executing workflow: {workflow_id}")
    
    async def execute_workflow():
        try:
            # Load workflow definition
            with open(workflow_file, 'r') as f:
                workflow_data = json.load(f)
            
            orchestrator = MultiAgentOrchestrator()
            
            # Create workflow
            await orchestrator.create_workflow(
                workflow_id=workflow_id,
                agents=workflow_data.get("agents", []),
                steps=workflow_data.get("steps", [])
            )
            
            # Execute workflow
            input_data = workflow_data.get("input_data", {})
            results = await orchestrator.execute_workflow(workflow_id, input_data)
            
            click.echo(f"✅ Workflow completed successfully!")
            click.echo(f"Results: {json.dumps(results, indent=2)}")
            
        except Exception as e:
            click.echo(f"❌ Workflow failed: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(execute_workflow())

# Utility Commands
@cli.command()
def status():
    """Show system status and health."""
    click.echo("🏥 System Status Check")
    
    async def check_status():
        try:
            # Check trust manager
            trust_manager = ZippyTrustManager()
            secure_manager = SecurePluginManager()
            marketplace = ZippyCoinMarketplace()
            
            # Get trust summary
            trust_summary = secure_manager.get_trust_summary()
            marketplace_stats = marketplace.get_marketplace_stats()
            
            click.echo(f"\n🛡️  Trust System:")
            click.echo(f"   Total Plugins: {trust_summary['total_plugins']}")
            click.echo(f"   Trusted Plugins: {trust_summary['trusted_plugins']}")
            click.echo(f"   Blocked Plugins: {trust_summary['blocked_plugins']}")
            click.echo(f"   Average Trust Score: {trust_summary['average_trust_score']:.2f}")
            click.echo(f"   Trust Verification: {'✅ Enabled' if trust_summary['trust_verification_enabled'] else '❌ Disabled'}")
            
            click.echo(f"\n🛒 Marketplace:")
            click.echo(f"   Total Listings: {marketplace_stats['total_listings']}")
            click.echo(f"   Active Listings: {marketplace_stats['active_listings']}")
            click.echo(f"   Total Downloads: {marketplace_stats['total_downloads']}")
            click.echo(f"   Total Volume: {marketplace_stats['total_volume_zippycoin']:.2f} ZC")
            click.echo(f"   Average Trust Score: {marketplace_stats['average_trust_score']:.2f}")
            
            click.echo(f"\n✅ All systems operational!")
            
        except Exception as e:
            click.echo(f"❌ Status check failed: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(check_status())

@cli.command()
@click.option('--output', '-o', type=click.Path(), help='Output file for report')
def report(output: Optional[str]):
    """Generate a comprehensive system report."""
    click.echo("📊 Generating system report...")
    
    async def generate_report():
        try:
            trust_manager = ZippyTrustManager()
            secure_manager = SecurePluginManager()
            marketplace = ZippyCoinMarketplace()
            
            # Collect data
            trust_summary = secure_manager.get_trust_summary()
            marketplace_stats = marketplace.get_marketplace_stats()
            trusted_plugins = trust_manager.list_trusted_plugins()
            
            # Generate report
            report_data = {
                "generated_at": datetime.now().isoformat(),
                "trust_system": {
                    "summary": trust_summary,
                    "trusted_plugins": [
                        {
                            "plugin_id": p.plugin_id,
                            "author": p.author,
                            "trust_score": p.zippy_trust_score,
                            "status": p.verification_status,
                            "version": p.version
                        }
                        for p in trusted_plugins
                    ]
                },
                "marketplace": marketplace_stats,
                "recommendations": []
            }
            
            # Add recommendations
            if trust_summary['average_trust_score'] < 0.7:
                report_data["recommendations"].append("Consider improving plugin code quality")
            
            if marketplace_stats['total_listings'] < 10:
                report_data["recommendations"].append("Encourage more plugin submissions")
            
            if trust_summary['blocked_plugins'] > 0:
                report_data["recommendations"].append("Review blocked plugins for potential improvements")
            
            # Display report
            click.echo(f"\n📈 System Report")
            click.echo(f"   Generated: {report_data['generated_at']}")
            click.echo(f"   Trust Score: {trust_summary['average_trust_score']:.2f}")
            click.echo(f"   Marketplace Health: {'Good' if marketplace_stats['active_listings'] > 5 else 'Needs Attention'}")
            click.echo(f"   Recommendations: {len(report_data['recommendations'])}")
            
            # Save report if requested
            if output:
                with open(output, 'w') as f:
                    json.dump(report_data, f, indent=2)
                click.echo(f"\n💾 Report saved to: {output}")
            
        except Exception as e:
            click.echo(f"❌ Report generation failed: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(generate_report())

# Helper functions
def extract_plugin_metadata(plugin_code: str, filename: str) -> PluginMetadata:
    """Extract metadata from plugin code (simplified version)."""
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
            deps_str = line.split('=')[1].strip()
            if deps_str.startswith('[') and deps_str.endswith(']'):
                dependencies = [d.strip().strip('"\'') for d in deps_str[1:-1].split(',')]
        elif line.startswith('tags ='):
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

if __name__ == '__main__':
    cli()
