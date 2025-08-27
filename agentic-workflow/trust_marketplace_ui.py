# trust_marketplace_ui.py

import streamlit as st
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from plugins.trust_manager import ZippyTrustManager, TrustScore, PluginMetadata
from plugins.secure_plugin_manager import SecurePluginManager
from plugins.marketplace import ZippyCoinMarketplace, PluginListing, ZippyCoinClient

# Page configuration
st.set_page_config(
    page_title="ZippyTrust & Marketplace",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize managers
@st.cache_resource
def get_managers():
    trust_manager = ZippyTrustManager()
    secure_plugin_manager = SecurePluginManager()
    marketplace = ZippyCoinMarketplace()
    return trust_manager, secure_plugin_manager, marketplace

trust_manager, secure_plugin_manager, marketplace = get_managers()

# Sidebar
st.sidebar.title("🛡️ ZippyTrust & Marketplace")
st.sidebar.markdown("---")

# User wallet management
st.sidebar.subheader("💰 ZippyCoin Wallet")
wallet_address = st.sidebar.text_input("Wallet Address", placeholder="Enter your ZippyCoin wallet address")

if wallet_address:
    # Get wallet balance
    async def get_balance():
        async with ZippyCoinClient() as client:
            return await client.get_balance(wallet_address)
    
    balance = asyncio.run(get_balance())
    st.sidebar.metric("Balance", f"{balance:.2f} ZC")
else:
    st.sidebar.info("Enter your wallet address to view balance and make purchases")

# Trust settings
st.sidebar.subheader("🔒 Trust Settings")
trust_threshold = st.sidebar.slider("Trust Threshold", 0.0, 1.0, 0.7, 0.1)
secure_plugin_manager.update_trust_threshold(trust_threshold)

trust_verification = st.sidebar.checkbox("Enable Trust Verification", value=True)
secure_plugin_manager.trust_verification = trust_verification

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["🛡️ Trust Dashboard", "🛒 Marketplace", "📦 My Plugins", "📊 Analytics"])

# Tab 1: Trust Dashboard
with tab1:
    st.title("🛡️ ZippyTrust Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Trust summary
    trust_summary = secure_plugin_manager.get_trust_summary()
    
    with col1:
        st.metric("Total Plugins", trust_summary["total_plugins"])
    
    with col2:
        st.metric("Trusted Plugins", trust_summary["trusted_plugins"])
    
    with col3:
        st.metric("Blocked Plugins", trust_summary["blocked_plugins"])
    
    with col4:
        st.metric("Avg Trust Score", f"{trust_summary['average_trust_score']:.2f}")
    
    st.markdown("---")
    
    # Plugin trust details
    st.subheader("📋 Plugin Trust Details")
    
    if trust_summary["total_plugins"] > 0:
        # Create trust data for visualization
        trust_data = []
        for tool_name, trust_score in secure_plugin_manager.trust_scores.items():
            trust_data.append({
                "Plugin": tool_name,
                "Trust Score": trust_score.zippy_trust_score,
                "Status": trust_score.verification_status,
                "Author": trust_score.author,
                "Version": trust_score.version,
                "Last Updated": trust_score.last_updated
            })
        
        df = pd.DataFrame(trust_data)
        
        # Trust score distribution
        fig = px.histogram(df, x="Trust Score", nbins=10, title="Trust Score Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        # Trust status breakdown
        status_counts = df["Status"].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, title="Plugin Status Breakdown")
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.dataframe(df, use_container_width=True)
        
        # Trust score by author
        author_trust = df.groupby("Author")["Trust Score"].mean().sort_values(ascending=False)
        fig = px.bar(x=author_trust.index, y=author_trust.values, title="Average Trust Score by Author")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No plugins loaded yet. Load some plugins to see trust information.")

# Tab 2: Marketplace
with tab2:
    st.title("🛒 ZippyCoin Plugin Marketplace")
    
    # Search and filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("Search plugins", placeholder="Enter plugin name or description")
    
    with col2:
        min_trust = st.slider("Minimum Trust Score", 0.0, 1.0, 0.0, 0.1)
    
    with col3:
        max_price = st.number_input("Maximum Price (ZC)", min_value=0.0, value=100.0, step=1.0)
    
    # Search plugins
    plugins = marketplace.search_plugins(
        query=search_query,
        min_trust=min_trust,
        max_price=max_price
    )
    
    if plugins:
        st.subheader(f"Found {len(plugins)} plugins")
        
        # Display plugins in cards
        for i, plugin in enumerate(plugins):
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"### {plugin.name}")
                    st.markdown(f"**{plugin.description}**")
                    st.markdown(f"Author: {plugin.author} | Version: {plugin.version}")
                    st.markdown(f"Tags: {', '.join(plugin.tags)}")
                
                with col2:
                    # Trust badge
                    trust_color = "green" if plugin.trust_score >= 0.8 else "orange" if plugin.trust_score >= 0.6 else "red"
                    st.markdown(f"<div style='color: {trust_color}; font-weight: bold;'>🛡️ {plugin.trust_score:.2f}</div>", unsafe_allow_html=True)
                    
                    st.markdown(f"⭐ {plugin.rating:.1f}")
                    st.markdown(f"📥 {plugin.download_count}")
                
                with col3:
                    st.markdown(f"**{plugin.price_zippycoin} ZC**")
                    
                    if wallet_address:
                        if st.button(f"Buy", key=f"buy_{i}"):
                            with st.spinner("Processing purchase..."):
                                result = asyncio.run(marketplace.purchase_plugin(plugin.plugin_id, wallet_address))
                                if result["success"]:
                                    st.success(result["message"])
                                    st.rerun()
                                else:
                                    st.error(f"Purchase failed: {result['error']}")
                    else:
                        st.info("Enter wallet to purchase")
                
                st.markdown("---")
    else:
        st.info("No plugins found matching your criteria.")
    
    # Marketplace stats
    st.subheader("📊 Marketplace Statistics")
    stats = marketplace.get_marketplace_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Listings", stats["total_listings"])
    with col2:
        st.metric("Active Listings", stats["active_listings"])
    with col3:
        st.metric("Total Downloads", stats["total_downloads"])
    with col4:
        st.metric("Total Volume", f"{stats['total_volume_zippycoin']:.2f} ZC")

# Tab 3: My Plugins
with tab3:
    st.title("📦 My Plugins")
    
    if wallet_address:
        # User's purchased plugins
        purchases = marketplace.get_user_purchases(wallet_address)
        
        if purchases:
            st.subheader("🛒 Purchase History")
            purchase_data = []
            for purchase in purchases:
                purchase_data.append({
                    "Plugin": purchase.plugin_id,
                    "Amount": purchase.amount,
                    "Date": purchase.timestamp,
                    "Status": purchase.status
                })
            
            df_purchases = pd.DataFrame(purchase_data)
            st.dataframe(df_purchases, use_container_width=True)
        else:
            st.info("No purchase history found.")
        
        # User's authored plugins
        authored_plugins = marketplace.get_author_plugins(wallet_address)
        
        if authored_plugins:
            st.subheader("✍️ My Authored Plugins")
            
            for plugin in authored_plugins:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"### {plugin.name}")
                        st.markdown(f"**{plugin.description}**")
                        st.markdown(f"Status: {plugin.status}")
                    
                    with col2:
                        st.markdown(f"🛡️ {plugin.trust_score:.2f}")
                        st.markdown(f"📥 {plugin.download_count}")
                    
                    with col3:
                        st.markdown(f"**{plugin.price_zippycoin} ZC**")
                        
                        if st.button(f"Edit", key=f"edit_{plugin.plugin_id}"):
                            st.info("Edit functionality coming soon...")
                        
                        if st.button(f"Remove", key=f"remove_{plugin.plugin_id}"):
                            if marketplace.remove_plugin_listing(plugin.plugin_id, wallet_address):
                                st.success("Plugin removed from marketplace")
                                st.rerun()
                            else:
                                st.error("Failed to remove plugin")
                    
                    st.markdown("---")
        else:
            st.info("No authored plugins found.")
    else:
        st.info("Enter your wallet address to view your plugins.")

# Tab 4: Analytics
with tab4:
    st.title("📊 Analytics Dashboard")
    
    # Trust analytics
    st.subheader("🛡️ Trust Analytics")
    
    if secure_plugin_manager.trust_scores:
        trust_scores = list(secure_plugin_manager.trust_scores.values())
        
        # Trust score trends
        trust_data = []
        for score in trust_scores:
            trust_data.append({
                "Plugin": score.plugin_id,
                "Trust Score": score.zippy_trust_score,
                "Code Quality": score.code_quality_score,
                "Security": score.security_checks.get("code_analysis", False),
                "Author": score.author
            })
        
        df_trust = pd.DataFrame(trust_data)
        
        # Trust score vs code quality
        fig = px.scatter(df_trust, x="Code Quality", y="Trust Score", 
                        hover_data=["Plugin", "Author"], 
                        title="Trust Score vs Code Quality")
        st.plotly_chart(fig, use_container_width=True)
        
        # Author performance
        author_performance = df_trust.groupby("Author").agg({
            "Trust Score": ["mean", "count"],
            "Code Quality": "mean"
        }).round(3)
        
        st.subheader("👥 Author Performance")
        st.dataframe(author_performance, use_container_width=True)
    
    # Marketplace analytics
    st.subheader("🛒 Marketplace Analytics")
    
    if marketplace.listings:
        # Price distribution
        prices = [plugin.price_zippycoin for plugin in marketplace.listings.values()]
        fig = px.histogram(x=prices, nbins=10, title="Plugin Price Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        # Trust score vs price
        price_trust_data = []
        for plugin in marketplace.listings.values():
            price_trust_data.append({
                "Price": plugin.price_zippycoin,
                "Trust Score": plugin.trust_score,
                "Downloads": plugin.download_count,
                "Plugin": plugin.name
            })
        
        df_price_trust = pd.DataFrame(price_trust_data)
        fig = px.scatter(df_price_trust, x="Price", y="Trust Score", 
                        size="Downloads", hover_data=["Plugin"],
                        title="Price vs Trust Score (size = downloads)")
        st.plotly_chart(fig, use_container_width=True)
    
    # System health
    st.subheader("🏥 System Health")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Trust Verification", "✅ Enabled" if trust_verification else "❌ Disabled")
        st.metric("Cache Status", "✅ Active")
        st.metric("API Status", "✅ Connected")
    
    with col2:
        st.metric("Blocked Plugins", trust_summary["blocked_plugins"])
        st.metric("Average Trust", f"{trust_summary['average_trust_score']:.2f}")
        st.metric("Security Level", "High" if trust_threshold >= 0.8 else "Medium" if trust_threshold >= 0.6 else "Low")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🛡️ ZippyTrust & 🪙 ZippyCoin Integration | 
        Built with ❤️ for secure plugin management
    </div>
    """, 
    unsafe_allow_html=True
)
