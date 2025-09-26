#!/usr/bin/env python3
"""
Simple wrapper to provide direct access to enhanced stock analysis tools
without agent complexity. This ensures users always get real Yahoo Finance data.
"""

import os
import re
from pathlib import Path
import tools

def load_env_file():
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

load_env_file()

def process_query(query):
    """
    Process user queries and route them to appropriate tools
    """
    query_lower = query.lower().strip()
    
    # Extract company name from query
    company_patterns = [
        r"(?:analyze|analysis of|get info for|details for|screen|check)\s+([^,\.]+?)(?:\s|$|,|\.|with|and)",
        r"(?:company|stock|share)\s+([^,\.]+?)(?:\s|$|,|\.|with|and)",
        r"([a-zA-Z][a-zA-Z\s&\.,-]+?)(?:\s+(?:stock|share|company)|$)"
    ]
    
    company_name = None
    for pattern in company_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            company_name = match.group(1).strip()
            # Clean up common words
            company_name = re.sub(r'\b(inc|corp|corporation|ltd|limited|company|co)\b\.?', '', company_name, flags=re.IGNORECASE).strip()
            if len(company_name) > 2:  # Valid company name
                break
    
    if not company_name:
        return "❌ Could not identify company name in your query. Please try: 'Analyze Apple' or 'Screen Microsoft'"
    
        print(f"Processing query for: {company_name}")
    
    # Determine action type
    if any(word in query_lower for word in ['screen', 'check threshold', 'add to watchlist', 'criteria']):
        print("Using screening analysis with thresholds...")
        return tools.screen_and_add(company_name)
    
    elif any(word in query_lower for word in ['analyze', 'analysis', 'details', 'info', 'comprehensive']):
        print("Using comprehensive analysis...")
        return tools.analyze_stock(company_name)
    
    else:
        # Default to comprehensive analysis
        print("📈 Using comprehensive analysis (default)...")
        return tools.analyze_stock(company_name)

def process_watchlist_query(query):
    """Process watchlist-related queries"""
    query_lower = query.lower().strip()
    
    if 'show' in query_lower or 'list' in query_lower or 'display' in query_lower:
        watchlist = tools.show_watchlist()
        if not watchlist:
            return "📋 Your watchlist is empty."
        
        result = f"Your Watchlist ({len(watchlist)} stocks):\n\n"
        for symbol in watchlist:
            details = tools.get_detailed_stock_info(symbol)
            if 'error' not in details:
                # Show first few lines of analysis
                lines = details['formatted_info'].split('\n')[:8]
                result += '\n'.join(lines) + '\n\n' + '='*50 + '\n\n'
            else:
                result += f"ERROR loading {symbol}: {details.get('error', 'Unknown error')}\n\n"
        return result
    
    elif 'clear' in query_lower:
        return tools.clear_watchlist()
    
    else:
        return "❓ Watchlist commands: 'show watchlist', 'clear watchlist'"

def smart_stock_query(user_input):
    """
    Smart query processor that routes to appropriate tools
    """
    if not user_input or not user_input.strip():
        return "❓ Please enter a query like: 'Analyze Apple' or 'Screen Microsoft'"
    
    query = user_input.strip()
    
    # Check for watchlist queries
    if 'watchlist' in query.lower():
        return process_watchlist_query(query)
    
    # Check for threshold queries
    if 'threshold' in query.lower() and 'set' in query.lower():
        # Extract ROE and PEG values
        numbers = re.findall(r'\d+\.?\d*', query)
        if len(numbers) >= 2:
            try:
                roe = float(numbers[0])
                peg = float(numbers[1])
                return tools.set_thresholds(roe, peg)
            except:
                pass
        return "❓ To set thresholds, use: 'Set thresholds ROE 20 PEG 1.5'"
    
    if 'threshold' in query.lower() and ('show' in query.lower() or 'get' in query.lower()):
        thresholds = tools.get_thresholds()
        return f"Current Thresholds: ROE > {thresholds.get('roe', 15)}%, PEG < {thresholds.get('peg', 2)}"
    
    # Process stock analysis queries
    return process_query(query)

if __name__ == "__main__":
    print("🚀 Enhanced Stock Analysis Tool")
    print("=" * 50)
    print("Available commands:")
    print("• 'Analyze [Company]' - Comprehensive analysis")
    print("• 'Screen [Company]' - Analysis with threshold check")
    print("• 'Show watchlist' - Display watchlist with details")
    print("• 'Set thresholds ROE 20 PEG 1.5' - Update criteria")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n💬 Enter your query (or 'quit' to exit): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            result = smart_stock_query(user_input)
            print(f"\nResult:\n{result}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")