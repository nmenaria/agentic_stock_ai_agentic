#!/usr/bin/env python3
"""
Final demo of the working agent
"""
import os
from agentic_app import agent

print("🚀 Agentic Stock AI - Final Demo")
print("=" * 50)

# Test queries
queries = [
    "Screen Apple and show me the fundamentals",
    "Add Microsoft to watchlist", 
    "Show current watchlist",
    "Set thresholds to ROE 20, PEG 1.5"
]

for i, query in enumerate(queries, 1):
    print(f"\n📋 Query {i}: {query}")
    print("-" * 30)
    
    try:
        # Use invoke instead of run to avoid deprecation warnings
        result = agent.invoke({"input": query})
        output = result.get("output", "No output")
        print(f"✅ Response: {output}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("🎉 Demo complete! Your agent is working!")
print("💡 Run 'streamlit run streamlit_app.py' for the web interface.")